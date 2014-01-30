from nose.tools import eq_
from domainmodeller import celeryconfig
from domainmodeller.TaskHub import TaskHub
from storage_template import db_eq, add_detached
from domainmodeller.storage.schema import Paper, PaperTerm

from .storage_template import storage, solr

s = storage.session()

# Mock the lemmatizer because it loads WordNet into memory on first use,
# and ends up almost doubling the time it takes to run all tests.
def mock_lemmatizer(word):
    if word.endswith('s') and word != 'linguistics':
        return word[:-1]
    return word
from domainmodeller.util import nlp_util
nlp_util._lemmatizer = mock_lemmatizer
    

# Run celery tasks in local mode
celeryconfig.CELERY_ALWAYS_EAGER = True

term1, t_nl = 'part-of-speech taggers', 'part_of_speech_tagger'
term2, t_nlp = 'computational Linguistics', 'computational_linguistics'

paper1 = Paper(
    id=1,
    raw_text='algorithm for %s. program for %s' % (term1, term1),
    url_private='http://testdocument',
    flag_text_extraction_ok=True,
)
paper2 = Paper(
    id=2,
    title='Second paper',
    raw_text='principle for %s. program for %s (CL)' % (term1, term2),
    url_private='http://testdocument',
    flag_text_extraction_ok=True,
)

def setUpModule():
    storage.clear()
    docs = [paper1, paper2]
    add_detached(docs)
    
    task_hub = TaskHub(storage, solr)
    task_hub.run('extract_terms')

    '''
    from storage_template import generate_tests
    generate_tests(s, Paper, 'id')
    generate_tests(s, PaperTerm, 'id')
    #'''

###### Paper object tests (auto-generated)

def test_count_paper():
    eq_(2, s.query(Paper).count())

def test_paper_1():
    actual = s.query(Paper).filter(Paper.id==1L).one()
    expected = Paper(
        id=1L,
        url_private=u'http://testdocument',
        raw_text=u'algorithm for part-of-speech taggers. program for part-of-speech taggers',
        flag_text_extraction_ok=True,
        flag_text_extraction_failed=False,
        flag_term_extraction_ok=True,
    )
    db_eq(expected, actual)

def test_paper_2():
    actual = s.query(Paper).filter(Paper.id==2L).one()
    expected = Paper(
        id=2L,
        url_private=u'http://testdocument',
        title=u'Second paper',
        raw_text=u'principle for part-of-speech taggers. program for computational Linguistics (CL)',
        flag_text_extraction_ok=True,
        flag_text_extraction_failed=False,
        flag_term_extraction_ok=True,
    )
    db_eq(expected, actual)


###### PaperTerm object tests (auto-generated)

def test_count_paperterm():
    eq_(3, s.query(PaperTerm).count())

def test_paperterm_1():
    actual = s.query(PaperTerm).filter(PaperTerm.id==1L).one()
    expected = PaperTerm(
        id=1L,
        paper_id=1L,
        term_string=u'part-of-speech taggers',
        topic_slug=u'part_of_speech_tagger',
        matches=2L,
        pattern=u'JJ NNS',
    )
    db_eq(expected, actual)

def test_paperterm_2():
    actual = s.query(PaperTerm).filter(PaperTerm.id==2L).one()
    expected = PaperTerm(
        id=2L,
        paper_id=2L,
        term_string=u'computational Linguistics',
        topic_slug=u'computational_linguistics',
        matches=1L,
        pattern=u'NN NNP',
        acronym=u'CL',
    )
    db_eq(expected, actual)

def test_paperterm_3():
    actual = s.query(PaperTerm).filter(PaperTerm.id==3L).one()
    expected = PaperTerm(
        id=3L,
        paper_id=2L,
        term_string=u'part-of-speech taggers',
        topic_slug=u'part_of_speech_tagger',
        matches=1L,
        pattern=u'JJ NNS',
    )
    db_eq(expected, actual)

