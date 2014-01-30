# coding: utf-8
from domainmodeller.topicstats import topicstats

import unittest
from nose.tools import eq_

from domainmodeller.util.nlp_util import topic_occ_tokenizer
tokenizer = topic_occ_tokenizer()

txt = u'''
alignment space Ontology similarity ngram in the alignment space space alignment in semantic alignment space
thing alignment. space something Ondrˇej web'''.strip()

class TestFindSpanTerms(unittest.TestCase):
    '''
    Test for the following:
    - Unicode term
    - Single word term
    - Term at start of document
    - Term in middle of document
    - Term at end of document.
    - Embedded term
    - Partially embedded term
    - Works across line breaks
    - Terms are not found between sentence boundaries
      (implicitly tested by adding a '.' between terms)
    '''
    
    @classmethod
    def setup_class(cls):
        w = topicstats.WordTrie()
        w.add(['ngram'], 'as')
        w.add(['alignment', 'space'], 'as')
        w.add(['alignment', 'space', 'thing'], 'ast')
        w.add([u'ondrˇej', 'web'], 'ow')
        w.add([u'semantic', 'alignment'], 'sa')
        
        tokens = tokenizer(txt, chars=True)

        cls.output = list(w.find_span_terms(tokens))

    def test_term_count(self):
        eq_(7, len(self.output))
        
    def test_start_term(self):
        eq_(('as', 0, len('alignment space')), self.output[0])
    
    def test_one_word_term(self):
        eq_(('as', 36, 36+len('ngram')), self.output[1])
        
    def test_middle_term(self):
        eq_(('as', 49, 49+len('alignment space')), self.output[2])
    
    def test_partially_embedded_term(self):
        eq_(('sa', 84, 84+len('semantic alignment')), self.output[3])
        
    def test_embedded_inner_term(self):
        eq_(('as', 93, 93+len('alignment space')), self.output[4])
    
    def test_embedded_outer_term(self):
        eq_(('ast', 93, 93+len('alignment space\nthing')), self.output[5])
        
    def test_unicode_and_end_term(self):
        eq_(('ow', 142, 142+len(u'Ondrˇej web')), self.output[6])

