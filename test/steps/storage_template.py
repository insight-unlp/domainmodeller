'''Test utilities'''

from . import settings

from domainmodeller.storage import Storage, schema
from sqlalchemy.orm import session
from sqlalchemy.orm.util import class_mapper
import re
storage = Storage.init_storage(settings.DATABASE, **settings.BACKEND)
solr = Storage.init_solr(settings.DATABASE, settings.SOLR_ROOT)

from domainmodeller.storage.schema import PaperTerm, Paper, Topic

from pprint import pformat
from nose.tools import eq_

def generate_tests(s, clazz, *retrieval_keys):
    '''Utility for generating tests that compare database objects in a given table
    (clazz). :retrieval_key is the name of the column in clazz that can uniquely
    fetch the object.'''
    test_strings = []
    
    test_strings.append('\n###### %s object tests (auto-generated)' % (clazz.__name__))
    
    class_name = clazz.__name__
    
    # Make a count test to ensure there are no unexpected objects
    count = s.query(clazz).count()
    test_string = ['def test_count_%s():' % class_name.lower()]
    test_string.append('\teq_(%s, s.query(%s).count())' % (count, class_name))
    test_strings.append('\n'.join(test_string))
    
    for record in s.query(clazz):
        key_vals = [getattr(record, k) for k in retrieval_keys]
        
        # Name the function
        joined_keys = '_'.join(map(str, key_vals))
        fn_suffix = re.sub('[^0-9a-zA-Z_]', '_', joined_keys)

        # Create expected record
        lines = repr(record).split('\n')

        # Replace auto-incrementing primary key with reference to actual, since they
        # may not be consistent across tests.
        def replace_pks(lines):
            for pk in schema.get_integer_primary_keys(clazz):
                for line in lines:
                    if line.startswith('\t%s='%pk.name):
                        yield '\t%s=actual.id,' % pk.name
                    else:
                        yield line
        lines = list(replace_pks(lines))
                
        indented_record = '\n\t'.join(lines)
        
        test_str = ['def test_%s_%s():' % (class_name.lower(), fn_suffix)]
        filters = ['%s.%s==%s'%(class_name, r, repr(k)) for r,k in zip(retrieval_keys, key_vals)]
        test_str.append('\tactual = s.query(%s).filter(%s).one()' % \
                (class_name, ', '.join(filters)))
        test_str.append('\texpected = %s' % indented_record)
        test_str.append('\tdb_eq(expected, actual)')
        test_strings.append('\n'.join(test_str))
        
    print '\n\n'.join(test_strings) + '\n'
    

def add_detached(docs):
    s = storage.session()
    s.add_all(docs)
    s.commit()
    disconnect_from_db(docs)
    s.close()

def _normalize_types(dictionary):
    '''Different backends have different properties, some will return Long instead of
    Int etc. Normalise for these differences when comparing.'''
    for k, v in dictionary.items():
        if isinstance(v, int):
            dictionary[k] = long(v)
        elif isinstance(v, float):
            dictionary[k] = round(v, 5)

def db_eq(expected, actual):
    '''Compare two SQLAlchemy objects'''
    expected = expected.as_dict(include_none=False, include_unmapped=True)
    _normalize_types(expected)
    actual = actual.as_dict(include_none=False, include_unmapped=True)
    _normalize_types(actual)
    
    if not expected == actual:
        from difflib import unified_diff
        expected_str = pformat(dict(expected))
        actual_str = pformat(dict(actual))
        diff = '\n'.join(unified_diff(expected_str.split('\n'), actual_str.split('\n')))
        message = '\n%s\n!=\n%s\n\n%s' % (expected_str, actual_str, diff)
        eq_(expected, actual, message)

def disconnect_from_db(docs):
    '''Make sure that docs won't synchronise with the database if changed.'''
    for d in docs:
        #make_transient removes the primary keys, hack to back them up and
        #reset them after
        id_attrs = [a.name for a in class_mapper(d.__class__).primary_key]
        id_vals = {a: getattr(d, a) for a in id_attrs}
        
        session.make_transient(d)
        
        for attr, val in id_vals.iteritems():
            setattr(d, attr, val)

class Utils:
    
    def __init__(self, storage):
        self.s = storage.session()
    
    def get_paper(self, paper_id):
        return self.s.query(Paper).filter(Paper.id==paper_id).one()
    
    def get_paper_term(self, paper_id, term_string):
        return self.s.query(PaperTerm) \
          .filter(PaperTerm.paper_id==paper_id, PaperTerm.term_string==term_string).one()
    
    def get_topic(self, topic_id):
        return self.s.query(Topic).filter(Topic.id==topic_id).one()

utils = Utils(storage)  
