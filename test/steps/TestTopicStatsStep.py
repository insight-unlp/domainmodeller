from storage_template import db_eq, add_detached
from domainmodeller.storage.schema import Paper, Topic
from .storage_template import storage
from nose.tools import eq_
from domainmodeller.TaskHub import TaskHub

s = storage.session()

topic1_term, t_nl = 'computational Linguistics', 'computational_linguistics'
topic2_term1, t_nlp = 'part-of-speech taggers', 'part_of_speech_tagger'
# Test two morphological variations of the same topic
topic2_term2 = 'part-of speech tagger'

paper1 = Paper(id=1)
paper2 = Paper(id=2)
num_papers=2

t_nl = Topic(
    id=1,
    slug='natural_language',
    topic_string='Natural Language',
    word_count=2,
    matches=10,
    occurrences=25,
    paper_count=2,
)
t_nlp = Topic(
    id=2,
    slug='natural_language_processing',
    topic_string='Natural Language processing',
    word_count=3,
    matches=5,
    occurrences=15,
    paper_count=1,
)
t_anlp = Topic(
    id=3,
    slug='applied_natural_language_processing',
    topic_string='Applied Natural Language processing',
    word_count=3,
    matches=11,
    occurrences=9,
    paper_count=1,
)
t_filter = Topic(
    id=4,
    slug='filter_me',
    topic_string='Filter me',
    word_count=2,
    matches=1,
    occurrences=1,
    paper_count=2,
)

##################################################################################
# Note: The auto-generated tests were put in place once the previous
# tests were confirmed to be working and identical. By having the automated tests
# it is easy to know when the any output of the step changes, and if the change
# is expected and correct, then the tests can be regenerated.
##################################################################################


def setUpModule():
    storage.clear()
    add_detached([paper1, paper2])
    add_detached([t_nl, t_nlp, t_anlp, t_filter])

    task_hub = TaskHub(storage)
    # If tests change, look at the scores and set this accordingly so that the
    # intended topic gets filtered
    task_hub.run('topic_stats min_score=3.0')

    '''
    from storage_template import generate_tests
    generate_tests(s, Topic, 'slug'),
    generate_tests(s, FilteredTopic, 'slug')
    generate_tests(s, FilteredPaperTopic, 'paper_id', 'topic_id')
    #'''


###### Topic object tests (auto-generated)

def test_count_topic():
    eq_(3, s.query(Topic).count())

def test_topic_natural_language():
    actual = s.query(Topic).filter(Topic.slug==u'natural_language').one()
    expected = Topic(
        id=actual.id,
        slug=u'natural_language',
        topic_string=u'Natural Language',
        matches=10,
        occurrences=25,
        embeddedness=2,
        paper_count=2,
        word_count=2,
        score=8.640933555935126,
        flag_dbpedia_lookup_attempted=False,
        filtered=False,
    )
    db_eq(expected, actual)

def test_topic_natural_language_processing():
    actual = s.query(Topic).filter(Topic.slug==u'natural_language_processing').one()
    expected = Topic(
        id=actual.id,
        slug=u'natural_language_processing',
        topic_string=u'Natural Language processing',
        matches=5,
        occurrences=15,
        embeddedness=1,
        paper_count=1,
        word_count=3,
        score=7.801293539643973,
        flag_dbpedia_lookup_attempted=False,
        filtered=False,
    )
    db_eq(expected, actual)

def test_topic_applied_natural_language_processing():
    actual = s.query(Topic).filter(Topic.slug==u'applied_natural_language_processing').one()
    expected = Topic(
        id=actual.id,
        slug=u'applied_natural_language_processing',
        topic_string=u'Applied Natural Language processing',
        matches=11,
        occurrences=9,
        embeddedness=0,
        paper_count=1,
        word_count=3,
        score=7.4547199493640015,
        flag_dbpedia_lookup_attempted=False,
        filtered=False,
    )
    db_eq(expected, actual)

