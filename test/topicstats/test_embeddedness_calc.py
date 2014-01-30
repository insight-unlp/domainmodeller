from domainmodeller.topicstats import topicstats

import unittest
from nose.tools import eq_, ok_

# Note: I'm using letters here for convenience, but this is intended
# for use with words.
topic_ids = [
    # nlp Embedded in nlpd, anlpt, anlp  
    # (for testing that left, center, and right embeddedness all work)
    'nlp',
    'anlp',
    'anlpt',
    'nlpd',
    # embedded in nothing
    'amp',
    # to test for length 1 in case of off-by-1 errors
    'p',
    # test that calculation is not affected by order added
    'lpd',
]

class MockTopic:
    def __init__(self, id_):
        self.id = id_

class TestEmbeddednessCalculator(unittest.TestCase):
    
    @classmethod
    def setup_class(cls):
        w = topicstats.EmbeddednessCalculator()
        
        for t in topic_ids:
            w.add(list(t), MockTopic(t))
        emb_map = w.calculate()
        
        cls.emb_map = {k: {t.id for t in v} for k,v in emb_map.iteritems()}

    def test_nlp(self):
        eq_(self.emb_map.get('nlp'), {'anlp', 'anlpt', 'nlpd'})

    def test_anlp(self):
        eq_(self.emb_map.get('anlp'), {'anlpt'})
        
    def test_anlpt(self):
        eq_(self.emb_map.get('anlpt'), None)
    
    def test_nlpd(self):
        eq_(self.emb_map.get('nlpd'), None)
        
    def test_amp(self):
        eq_(self.emb_map.get('amp'), None)
    
    def test_p(self):
        eq_(self.emb_map.get('p'), {'nlp', 'anlp', 'anlpt', 'nlpd', 'amp', 'lpd'})
        
    def test_lpd(self):
        eq_(self.emb_map.get('lpd'), {'nlpd'})