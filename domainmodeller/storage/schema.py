'''
Note: Always use two-column format for foreign key i.e.
     Column(Integer, ForeignKey(...)) 
   instead of
     Column(ForeignKey(...))

as current SQLAlchemy version does not store the foreign key in the column.foreign_keys
property otherwise.


Use integer primary keys where-ever possible, otherwise column indexes become huge and
slow.
'''

from sqlalchemy import Column, Integer, ForeignKey, Boolean, Float, String, Text

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.orm.properties import ColumnProperty
import types
import itertools
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import UniqueConstraint
import collections
import sqlalchemy

Base = declarative_base()

# Backend-specific overrides:
# Force mysql to use case-insensitive (utf8_bin) unicode

@compiles(String, 'mysql')
def compile_String_mysql(element, compiler, **kw):
    element.charset  = 'utf8'
    element.collation = 'utf8_bin'
    return compiler.visit_VARCHAR(element, **kw)

@compiles(Text, 'mysql')
def compile_text_mysql(element, compiler, **kw):
    element.charset  = 'utf8'
    element.collation = 'utf8_bin'
    # Use MEDIUMTEXT (16mb limit)
    return compiler.visit_MEDIUMTEXT(element, **kw)

# SQLAlchemy Utilities
def mapped_attrs(clazz):
    return [getattr(clazz, key) for key in mapped_attr_names(clazz)]

def column_size(column):
    return column.type.length

def mapped_attr_names(clazz):
    return [prop.key for prop in class_mapper(clazz).iterate_properties
                if isinstance(prop, ColumnProperty)]

def get_primary_keys(clazz):
    return class_mapper(clazz).primary_key

def get_integer_primary_keys(clazz):
    return [pk for pk in get_primary_keys(clazz) 
            if type(pk.type)==sqlalchemy.types.Integer]

def get_foreign_keys_to(column):
    '''Yields (mapped class, column with foreign key to :column)'''
    col = column.property.columns[0]
    for clazz in schema_classes:
        for fk_source, fk_dest in get_foreign_key_columns(clazz).iteritems():
            if id(fk_dest) == id(col):
                yield (clazz, fk_source)
            

def get_foreign_key_columns(clazz):
    '''Given a schema class, return {class column: foreign key class column}'''
    fk_cols = {}
    for column in class_mapper(clazz).columns:
        if column.foreign_keys:
            fk_cols[column] = next(iter(column.foreign_keys)).column
    return fk_cols

def copy_columns(source_class, target_class, excluded=['id']):
    for column in class_mapper(source_class).columns:
        my_col = column.copy()
        if my_col.name not in excluded:
            setattr(target_class, my_col.name, my_col)


class DictMixin(object):
    '''SQLALchemy mixin for converting entities to dictionaries.'''
    
    def __init__(self, *args, **kwargs):
        super(DictMixin, self).__init__(*args, **kwargs)
    
    def __get_unmapped_attributes(self, mapped_attributes):
        public_attrs = {d for d in dir(self) if d[0]!='_'}
        # Remove methods and special sqlalchemy attributes
        attrs = {pa for pa in public_attrs 
                 if type(getattr(self, pa)) != types.MethodType} - set(['metadata'])
        return attrs.difference(mapped_attributes)

    def as_dict(self, include_none=False, include_unmapped=False):
        '''Get an entity as a dictionary, for printing or comparing in tests.
        
        :include_unmapped SQLAlchemy does not throw an exception if an attribute is set
        that is not set in the class, e.g. if we do my_topic.something = 0 but
        'something' is not defined in the class, no error will be thrown. It is useful to
        include this attribute during unit tests so that the test will fail if the
        value did not actually end up in the database.
        '''
        mapped_attrs = mapped_attr_names(self.__class__)
        unmapped = []
        if include_unmapped:
            unmapped = self.__get_unmapped_attributes(mapped_attrs)
        
        doc = collections.OrderedDict()
        for prop in itertools.chain(mapped_attrs, unmapped):
            value = getattr(self, prop)
            if value is None and not include_none:
                continue
            doc[prop] = value 
        return doc

    def __repr__(self):
        thisdict = self.as_dict(include_none=False)
        args = '\n'.join('\t%s=%s,' % (k, repr(v)) for k, v in thisdict.iteritems())
        return '%s(\n%s\n)' % (self.__class__.__name__, args)

##### Papers

class Paper(DictMixin, Base):
    __tablename__ = 'Paper'
    id = Column(Integer, primary_key=True)
    slug = Column(String(100), unique=True, index=True)
    
    url_private = Column(String(255))
    title = Column(String(255))
    raw_text = Column(Text())
    domain_model = Column(String(60))
    
    flag_text_extraction_ok = Column(Boolean, default=False)
    flag_text_extraction_failed = Column(Boolean, default=False)
    flag_term_extraction_ok = Column(Boolean, default=False, index=True)

###### Terms and topics

class PaperTerm(DictMixin, Base):
    __tablename__ = 'PaperTerm'
    __table_args__ = (
        UniqueConstraint('paper_id', 'term_string'),
    )
    id = Column(Integer, primary_key=True)

    paper_id = Column(Integer, ForeignKey('Paper.id'))
    term_string = Column(String(150))
    topic_slug = Column(String(100), index=True)
    
    matches = Column(Integer)
    
    pattern = Column(String(30))
    acronym = Column(String(10))

class Topic(DictMixin, Base):
    __tablename__ = 'Topic'
    id = Column(Integer, primary_key=True)
    slug = Column(String(100), unique=True, index=True)
    
    topic_string = Column(String(100))
    matches = Column(Integer)
    occurrences = Column(Integer)
    acronym = Column(String(10))
    embeddedness = Column(Integer)
    paper_count = Column(Integer)
    word_count = Column(Integer)
    score = Column(Float)
    
    dbpedia_url = Column(String(300))
    dbpedia_disambiguation = Column(Boolean)
    
    flag_dbpedia_lookup_attempted = Column(Boolean, default=False)
    filtered = Column(Boolean, default=False, index=True)

# List of all schema class, useful for printing statistics etc.
schema_classes = [c for c in Base._decl_class_registry.values() 
                  if not c.__class__.__name__[0]=='_']
# Order schema classes by relation dependency
schema_classes = sorted(schema_classes)
