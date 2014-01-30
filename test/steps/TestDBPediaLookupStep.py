import unittest
from domainmodeller.TaskHub import TaskHub
from storage_template import utils, db_eq, add_detached,\
    storage
from domainmodeller.storage.schema import Topic
import httpretty
import re
import json
from domainmodeller.util.misc import get_package_path

from domainmodeller.steps.DBPediaLookupStep import DBPediaTitleMultiLookup
DBPediaTitleMultiLookup.PATCH_GEVENT = False

s = storage.session()

topic_string='Natural Language Processing'
dbpedia_id_real='Natural_language_processing'
# This one redirects to the real one 
dbpedia_id_redirect='Natural_Language_Processing'
dbpedia_url = u'http://dbpedia.org/resource/Natural_language_processing'

def get_mock_file(filename):
    with open(get_package_path('test', 'resources', filename)) as f:
        return f.read()

def mock_dbpedia_lookup(method, uri, headers):
    '''Mock the DBPedia lookup Solr service.'''
    if topic_string in uri.replace('+', ' '):
        response = {"response": {
            "docs": [
                {"title": dbpedia_id_real},
                {"title": dbpedia_id_redirect},
            ]
        }}
    else:
        response = {"response":{"numFound":0,"start":0,"docs":[]}}

    return (200, headers, json.dumps(response))

def mock_dbpedia_endpoint(method, uri, headers):
    '''Mock the DBPedia.org SPARQL endpoint.'''
    sparql = method.body

    response=None
    if 'wikiPageDisambiguates' in sparql:
        response = get_mock_file('dbpediamock2.json')    
    elif 'wikiPageRedirects' in sparql:
        response = get_mock_file('dbpediamock1.json')
    
    return (200, headers, response)


class MockDBPediaUtils:
    def find_redirect_pages(self, resources, titles_only=True):
        d = {}
        for r in resources:
            if r == dbpedia_id_redirect:
                d[topic_string] = [dbpedia_id_redirect]
        return d
    
    def find_disambiguation_pages(self, resources, titles_only=True):
        # Make it disambiguated just to check that the flag gets set
        return set([dbpedia_url])


class TestDBPediaLookup(unittest.TestCase):
    linked_topic = Topic(id=1, topic_string='Natural Language Processing')
    invalid_topic = Topic(id=2, topic_string='Some non-matching topic')

    @classmethod
    @httpretty.activate
    def setUpClass(cls):
        httpretty.register_uri(httpretty.GET, 
                           re.compile(r'http://dbpedia_service/(.*)'),
                           body=mock_dbpedia_lookup)
        httpretty.register_uri(httpretty.POST, 
                           re.compile(r'http://dbpedia.org/(.*)'),
                           body=mock_dbpedia_endpoint)
        
        storage.clear()
        add_detached([cls.linked_topic, cls.invalid_topic])

        from domainmodeller import settings
        settings.DBPEDIA_LOOKUP_SERVICE = 'http://dbpedia_service/'
        
        task_hub = TaskHub(storage, None)
        task_hub.run('dbpedia_lookup')

    def test_topic(self):
        actual = utils.get_topic(1)
        expected = self.linked_topic
        expected.dbpedia_url = dbpedia_url
        expected.dbpedia_disambiguation = True
        expected.flag_dbpedia_lookup_attempted = True
        db_eq(expected, actual)

    def test_topic_no_match(self):
        actual = utils.get_topic(2)
        expected = self.invalid_topic
        expected.dbpedia_url = None
        expected.flag_dbpedia_lookup_attempted = True
        db_eq(expected, actual)

