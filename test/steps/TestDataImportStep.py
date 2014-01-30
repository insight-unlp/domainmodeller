#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from .storage_template import storage
from domainmodeller.util import misc 
from nose.tools import eq_
from domainmodeller.storage.schema import Paper
from domainmodeller.TaskHub import TaskHub
from storage_template import db_eq

s = storage.session()
def setUpModule():
    storage.clear()
    sxf = misc.get_package_path('test', 'resources', 'dataimport')
    
    task_hub = TaskHub(storage)
    task_hub.run('import_directory ' + sxf)

    '''        
    from storage_template import generate_tests
    generate_tests(s, Paper, 'slug')
    #'''

###### Paper object tests (auto-generated)

def test_count_paper():
    eq_(2, s.query(Paper).count())

def test_paper_p1_txt():
    actual = s.query(Paper).filter(Paper.slug==u'p1.txt').one()
    expected = Paper(
        id=actual.id,
        slug=u'p1.txt',
        title=u'p1.txt',
        raw_text=u'Test paper 1',
        flag_text_extraction_ok=True,
        flag_text_extraction_failed=False,
        flag_term_extraction_ok=False,
    )
    db_eq(expected, actual)

def test_paper_p2_txt():
    actual = s.query(Paper).filter(Paper.slug==u'p2.txt').one()
    expected = Paper(
        id=actual.id,
        slug=u'p2.txt',
        title=u'p2.txt',
        raw_text=u'Test paper 2',
        flag_text_extraction_ok=True,
        flag_text_extraction_failed=False,
        flag_term_extraction_ok=False,
    )
    db_eq(expected, actual)


