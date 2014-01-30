import itertools
from domainmodeller.dbpedialookup import DBPediaUtils

import logging
log = logging.getLogger(__name__)

class DBPediaTopicMatcher:
    def __init__(self):
        self.dbp = DBPediaUtils.DBPediaUtils()
        
    def match_dbpedia_articles(self, topic2titles):
        '''Returns {topic2title: dbpedia_resource_url}+'''
        topic2titles = self.__remove_different_case(topic2titles)
        topic2titles = self.__replace_redirects(topic2titles)
        topic2titles = self.__remove_listof_pages(topic2titles)
        topic2titles = self.__remove_titled(topic2titles)
        
        return self.__pick_best_matches(topic2titles)
    
    def __remove_listof_pages(self, topic2titles):
        for topic, titles in topic2titles.iteritems():
            topic2titles[topic] = set(t for t in titles if not t.startswith('List_of'))
        return topic2titles
        
    def __has_same_case(self, topic, title):
        '''Checks if a topic and DBPedia title have the same case,
        excluding the first letter of each word. 
        e.g. 'bliss'=='Bliss' but 'bliss' != 'BLISS'
        ''' 
        topic_words = topic.split(' ')
        title_words = title.split('_')
        for topic_word, title_word in zip(topic_words, title_words):
            for c1, c2 in zip(topic_word, title_word)[1:]:
                if c1.lower() != c2.lower():
                    break
                if c1 != c2:
                    return False
    
        return True
    
    def __is_titled(self, s, delim=' '):
        return all(ss[0].isupper() for ss in s.split(delim))

    def __replace_redirects(self, topic2titles):
        '''Replace pages that redirect with the page that it redirects to'''
        all_matches = list(itertools.chain(*topic2titles.itervalues()))
        redirects_map = self.dbp.find_redirect_pages(all_matches)

        for topic, titles in topic2titles.iteritems():
            redirects = set()
            for t in titles:
                if t not in redirects_map:
                    redirects.add(t)
                else:
                    redirects.add(redirects_map[t])
            topic2titles[topic] = redirects
        return topic2titles

    def __remove_different_case(self, topic2titles):
        '''see __has_same_case'''
        for topic, titles in topic2titles.iteritems():
            topic2titles[topic] = set(t for t in titles if self.__has_same_case(topic, t))
        return topic2titles
    
    def __remove_titled(self, topic2titles):
        '''
        After removing redirect pages, pages with all words capitalised
        probably refer to something too specific. This removes those titled pages,
        unless it's the only available option or the topic itself is also titled.
        
        e.g. 
        'design patterns' -> ['Design_Patterns', 'Design_pattern']
        The former refers to a book so remove
        'User researchers' -> ['User_researchers', 'User_researcher']
        Former refers to a Windows feature, but since topic is capitalised, don't remove
        '''

        for k,v in topic2titles.iteritems():
            if not self.__is_titled(k) and len(v) > 1:
                topic2titles[k] = [a for a in v if not self.__is_titled(a, delim='_')]
        return topic2titles    

    def __pick_best_matches(self, topic2titles):
        all_matches = list(itertools.chain(*topic2titles.itervalues()))
        disambiguated = self.dbp.find_disambiguation_pages(all_matches, titles_only=False)
        
        result = {}
        def add_result(topic, title): 
            result[topic] = 'http://dbpedia.org/resource/' + title

        for topic, titles in topic2titles.iteritems():
            if not titles:
                continue
            elif len(titles) == 1:
                add_result(topic, iter(titles).next())
            else:
                # If exact match, choose that,
                for title in titles:
                    if title.replace('_', ' ').lower() == topic.lower():
                        add_result(topic, title)
                        break
                else:
                    # If only one is not a disambiguation page, pick that
                    non_disambiguated = disambiguated.difference(titles)
                    if len(non_disambiguated) == 1:
                        add_result(topic, iter(non_disambiguated).next())
                    else:
                        # PEP 20: In the face of ambiguity,
                        # refuse the temptation to guess :)
                        log.warn('"%s" has multiple matches: %s' % (topic, titles))
        
        return (disambiguated.intersection(result.values()), result)
