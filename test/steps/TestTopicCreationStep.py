from domainmodeller.TaskHub import TaskHub
from storage_template import storage, db_eq, add_detached
from domainmodeller.storage.schema import Paper, PaperTerm, Topic
from nose.tools import eq_
import unittest

topic1_term, t_nl = u'computational Linguistics', 'computational_linguistics'
topic2_term1, t_nlp = 'part-of-speech taggers', 'part_of_speech_tagger'
# Test two morphological variations of the same topic
topic2_term2 = 'part-of speech tagger'

paper1 = Paper(
    id=1,
    raw_text='algorithm for %s. program for %s' % (topic2_term1, topic2_term2),
    flag_term_extraction_ok=True
)
paper2 = Paper(
    id=2,
    raw_text='principle for %s. program for %s (CL)' % (topic2_term1, topic1_term),
    flag_term_extraction_ok=True
)

s = storage.session()

class TopicCreationTestBase(object):

    @classmethod
    def setup_class(cls):
        storage.clear()
    
        add_detached([paper1, paper2])
        add_detached([
            PaperTerm(
                paper_id=paper1.id,
                term_string=topic2_term1,
                topic_slug=t_nlp,
                matches=3
            ),
            PaperTerm(
                paper_id=paper1.id,
                term_string=topic2_term2,
                topic_slug=t_nlp,
                matches=2
            ),
            PaperTerm(
                paper_id=paper2.id,
                term_string=topic1_term,
                topic_slug=t_nl,
                matches=3,
                acronym='CL'
            ),
            # Leave out topic2_term1 so occurrence finder can find it
        ])
    
        task_hub = TaskHub(storage)
        task_hub.run('create_topics min_occ=1 use_hadoop=%s' % cls.use_hadoop)
    
        '''
        from storage_template import generate_tests
        generate_tests(s, Paper, 'id')
        generate_tests(s, PaperTopic, 'paper_id', 'topic_id')
        generate_tests(s, Topic, 'slug')
        #'''
        
    ###### Paper object tests (auto-generated)
    
    def test_count_paper(self):
        eq_(2, s.query(Paper).count())
    
    def test_paper_1(self):
        actual = s.query(Paper).filter(Paper.id==1).one()
        expected = Paper(
            id=1,
            raw_text=u'algorithm for part-of-speech taggers. program for part-of speech tagger',
            flag_text_extraction_ok=False,
            flag_text_extraction_failed=False,
            flag_term_extraction_ok=True,
        )
        db_eq(expected, actual)
    
    def test_paper_2(self):
        actual = s.query(Paper).filter(Paper.id==2).one()
        expected = Paper(
            id=2,
            raw_text=u'principle for part-of-speech taggers. program for computational Linguistics (CL)',
            flag_text_extraction_ok=False,
            flag_text_extraction_failed=False,
            flag_term_extraction_ok=True,
        )
        db_eq(expected, actual)
    
    ###### Topic object tests (auto-generated)
    
    def test_count_topic(self):
        eq_(2, s.query(Topic).count())
    
    def test_topic_computational_linguistics(self):
        actual = s.query(Topic).filter(Topic.slug==u'computational_linguistics').one()
        expected = Topic(
            id=1,
            slug=u'computational_linguistics',
            topic_string=u'Computational linguistics',
            matches=3,
            occurrences=1,
            acronym=u'CL',
            paper_count=1,
            word_count=2,
            filtered=False,
            flag_dbpedia_lookup_attempted=False,
        )
        db_eq(expected, actual)
    
    def test_topic_part_of_speech_tagger(self):
        actual = s.query(Topic).filter(Topic.slug==u'part_of_speech_tagger').one()
        expected = Topic(
            id=2,
            slug=u'part_of_speech_tagger',
            topic_string=u'Part-of-speech taggers',
            matches=5,
            occurrences=3,
            paper_count=2,
            word_count=4,
            filtered=False,
            flag_dbpedia_lookup_attempted=False,
        )
        db_eq(expected, actual)




# Hadoop is optional so we don't expect a user to have Hadoop set up,
# and this test takes a while to run. Uncomment if you are testing Luigi
#class TestTopicCreationHadoop(TopicCreationTestBase, unittest.TestCase):
#    use_hadoop=True

class TestTopicCreationLocal(TopicCreationTestBase, unittest.TestCase):
    use_hadoop=False
    
