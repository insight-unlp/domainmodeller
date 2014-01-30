# coding: utf-8
'''
==============================================================================
IN
==============================================================================
    Output of TopicCreationStep

==============================================================================
OUT
==============================================================================

::

    Topic += {
        embeddedness
        score            # Score for ranking. See score_topic() function
    }
    
    
'''

from IStep import IStep
from domainmodeller.task_logger import task_logger
import math
from domainmodeller.topicstats import topicstats
import logging
from domainmodeller.storage.schema import Topic
from domainmodeller.storage import storage_utils
log = logging.getLogger(__name__)

class TopicStatsStep(IStep):
    def run(self, s, min_score):
        topics = s.query(Topic).all()
        num_topics = len(topics)

        task_logger.info('Calculating embeddedness...')
        embeddedness_map = create_embeddedness_map(topics)
        calculate_embeddedness(topics, embeddedness_map)
        
        # Do this first so filtered topics are not counted in unembedded occurrences
        task_logger.info('Scoring topics...')
        num_filtered = self.score_topics(topics, num_topics, min_score)
        task_logger.info('Filtering %d topics...' % num_filtered)
        storage_utils.remove_filtered_topics(s)

        topics = s.query(Topic).all()

        for topic in topics:
            s.add(topic)

    def score_topics(self, topics, num_topics, min_score):
        num_filtered = 0
        for i, topic in enumerate(topics):
            topic.score = score_topic(topic)
            if topic.score < min_score:
                num_filtered += 1
                log.info('Filtering topic: Rank %.3f < %f: %s)'
                         % (topic.score, min_score, topic.topic_string))
                topic.filtered = True
            
            if (i+1)%1000==0:
                self.log_progress(i+1, num_topics, 'topics')
        return num_filtered

def create_embeddedness_map(topics):
    '''
    Scalability note: Currently we're building this in memory, the biggest dataset
    currently fits in a few hundred MB. If we ever need to process huge datasets
    where this doesn't fit comfortably in memory, this could be done via a database
    or Solr.
    '''
    emb_calc = topicstats.EmbeddednessCalculator()
    
    for topic in topics:
        tokens = topic.slug.split('_')
        emb_calc.add(tokens, topic)
    embeddedness_map = emb_calc.calculate()
    return embeddedness_map


def calculate_embeddedness(topics, embeddedness_map):
    for topic in topics:
        if topic.id in embeddedness_map:
            topic.embeddedness = len(embeddedness_map[topic.id])
        else:
            topic.embeddedness = 0

def score_topic(topic):
    emb = topic.embeddedness
    words = topic.word_count
    matches = topic.matches
    acronym_boost = 1 if topic.acronym else 0
    return words*math.log(1+matches) + 3.5*math.log(1+emb) + acronym_boost
    
