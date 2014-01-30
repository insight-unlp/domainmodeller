'''
This step finds a DBPedia URL for a topic from the topic string.

==============================================================================
IN
==============================================================================

::

    Topic = {
        topic_string
    }

==============================================================================
OUT
==============================================================================

::

    Topic = {
        flag_dbpedia_lookup_attempted = True
        dbpedia_url: http://dbpedia.org/resource/....
    }
    
'''

from domainmodeller.steps.IStep import IStep
from domainmodeller.task_logger import task_logger
from domainmodeller.dbpedialookup.DBPediaTopicMatcher import DBPediaTopicMatcher
from pprint import pprint
from domainmodeller.lookup_services import dbpedia_lookup 
from domainmodeller.storage.schema import Topic

class DBPediaLookupStep(IStep):

    def run(self, s, solr_url, num_topics, reset_all):
        if reset_all:
            s.query(Topic).update({
                Topic.dbpedia_url: None, 
                Topic.flag_dbpedia_lookup_attempted: False,
                Topic.dbpedia_disambiguation: False
            })

        topics = s.query(Topic)\
                 .filter(Topic.flag_dbpedia_lookup_attempted==False)\
                 .limit(num_topics)

        num_topics = topics.count()
        if num_topics == 0:
            task_logger.info('No topics to match.')
            return

        # 1. Query Solr DBPedia titles service to find candidate page titles from DBPedia.
        lookup_service = DBPediaTitleMultiLookup(solr_url)
        
        task_logger.info('Querying DBPedia titles look-up service...')
        #topic2titles: Map of topic string to candidate DBPedia titles.
        topic2titles = {}
        for i, (topic, titles) in enumerate(lookup_service.look_up_topics(topics)):
            if titles:
                topic_string = topic.topic_string
                topic2titles[topic_string] = titles
                self.log_progress(i+1, num_topics, word='topics',
                                      message='%s: %s' % (topic_string, titles))
        
        task_logger.info('%d out of %d topics matched one or more DBPedia titles' % 
                         (len(topic2titles), num_topics))
            
            
        # 2. We now actually go to DBPedia with the candidates list created above.
         
        task_logger.info('Matching DBPedia topics...')
        matcher = DBPediaTopicMatcher()
        #disambig: Set of matched pages which are disambiguation pages
        #topic2dbpedia_url: Dict of topic string to dbpedia resource url
        disambig, topic2dbpedia_url = matcher.match_dbpedia_articles(topic2titles)
        task_logger.info('Matched %d articles' % (len(topic2dbpedia_url)))
        pprint(topic2dbpedia_url)
        
        task_logger.info('Updating database...')
        for i, topic in enumerate(topics):
            if topic.topic_string in topic2dbpedia_url:
                topic.dbpedia_url =  topic2dbpedia_url[topic.topic_string]
                topic.dbpedia_disambiguation = topic.dbpedia_url in disambig
            topic.flag_dbpedia_lookup_attempted = True
            
            s.add(topic)
            if (i+1)%1000==0:
                s.flush()

class DBPediaTitleMultiLookup:
    '''Query the Solr service concurrently using gevent. gevent's co-routines are used
    instead of threads in case the service is running on the same host as the client,
    (single thread won't slow down the service's response time on a multi-core machine).
    '''
    
    # Needed for tests (HTTPretty and gevent patches conflict with each other.)
    PATCH_GEVENT = True
    
    def __init__(self, solr_url):
        self.lookup = dbpedia_lookup.DBPediaTitleLookup(solr_url)
        
    def look_up_topics(self, topics, pool_size=4):
        from gevent.pool import Pool
        if self.PATCH_GEVENT:
            from gevent import monkey
            monkey.patch_socket()
        
        pool = Pool(pool_size)
        for result in pool.imap_unordered(self._lookup_topic, topics):
            yield result 

    def _lookup_topic(self, topic):
        titles = self.lookup.query_minimal_stem(topic.topic_string)
        return topic, titles

