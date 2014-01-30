from nltk.corpus import wordnet as wn
import csv
import sys
from domainmodeller.steps.IStep import IStep
from domainmodeller.storage.schema import Topic
from domainmodeller.task_logger import task_logger


class EntityClassTask(IStep):
    
    def run(self, s):
        csvwriter = csv.writer(sys.stdout, delimiter=',', quoting=csv.QUOTE_NONE)
        
        for topic_string, score, pc in self.entity_class_topics_and_scores(s):
            csvwriter.writerow([topic_string, score, pc])
        
    def entity_class_topics_and_scores(self, s):
        # Get all one-word topics
        topics = s.query(Topic).order_by(Topic.score.desc()).filter(Topic.word_count==1)
        wn_filter = WordNetFilter()
         
        for topic in wn_filter.filter_many(topics): 
            yield topic.topic_string.lower(), topic.score, topic.paper_count
        
        from pprint import pformat
        task_logger.info('\nFiltered: \n%s' % pformat(wn_filter.filtered))

class WordNetFilter:
    
    def __init__(self):
        self.filtered = {'non-nouns': [], 'other': [], 'acronym': [], 'named-entities': []}
    
    def filter_many(self, topics):
        return (topic for topic in topics if not self.filter(topic))
    
    def filter(self, topic):
        '''Returns True if topic is filtered, False otherwise'''
        topic_string = topic.topic_string
        
        if len(topic_string) <= 2 or (topic.acronym and len(topic.acronym)==len(topic_string)):
            self.filtered['acronym'].append(topic_string)
            return True
        
        synsets = wn.synsets(topic_string, pos=wn.NOUN)

        if not synsets:
            self.filtered['non-nouns'].append(topic_string)
            return True
        
        synsets = self._filter_named_entity(synsets, topic_string)
        if not synsets:
            self.filtered['named-entities'].append(topic_string)
            return True

        synsets = self._filter_miscellaneous(synsets, topic_string)
        if not synsets:
            self.filtered['other'].append(topic_string)
            return True
        
        return False
    
    def _filter_non_noun(self, synsets, topic_string):
        if not synsets:
            self.filtered['non-nouns'].append(topic_string)
            return True
        return False
    
    def _filter_named_entity(self, synsets, topic_string):
        # Hacky attempt to remove named entities (we only want entity classes)
        return [s for s in synsets if not topic_string.title() in s.lemma_names()]
    
    def _filter_miscellaneous(self, synsets, topic_string):        
        invalid = ('noun.attribute', 'noun.time', 'noun.cognition')
        return [s for s in synsets if s.lexname not in invalid]
        
