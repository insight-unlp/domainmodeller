import pysolr
import re
from domainmodeller.util import misc 

class SolrStorage(object):
    '''Wraps the pysolr interface'''
    
    def begin(self):
        self.transaction = True
    
    def rollback(self):
        self.solr._update('<rollback />')
    
    def commit(self):
        self._solr.commit()
        self.transaction = False
    
    def __init__(self, host):
        self.transaction = False
        self._solr = pysolr.Solr(host)

    def index_all(self, type_, row_iterator):
        '''Index a table from the backend, deleting any existing records of that type.'''
        table_name = type_.__tablename__
        self.delete_type(table_name)
        
        self.begin()
        # Send the docs in chunks for speed
        for rows in misc.chunker(row_iterator, 1000):
            # Convert from schema format to Solr format
            self.add(rows)
        self.commit()
        

    def select(self, query, score=False, **kwargs):
        '''
        Returns an object with two properties:
          .docs is a list of returned document dictionaries
          .hits is the total number of hits for the query.
          
        If score=True, the Solr score is returned in the dictionary key.
        
        See PySolr docs/code for search() for other parameters.  
        '''
        if score:
            if 'fl' in kwargs:
                kwargs['fl'] = kwargs['fl'] + ',score'
            else:
                kwargs['fl'] = '*,score'
        
        if 'rows' not in kwargs:
            kwargs['rows'] = 1000000000
        return self._solr.search(query, **kwargs)

    REGEX_WORDS = re.compile(r'[^\s]+')
    
    def clear(self):
        '''Delete all Solr documents. WARNING: Cannot be undone!'''
        self._solr.delete(q='*:*')
        self._solr.commit()

    def delete_type(self, type_):
        self._solr.delete(q='type:%s' % type_)

    def __convert_mapped(self, entities):
        '''Convert SQLAlchemy mapped classes to Solr document format'''
        for entity in entities:
            doc = entity.as_dict(include_none=False)
            doc['type'] = entity.__tablename__
            yield doc

    def add(self, entities, **kwargs):
        '''
        Add/update iterable of SQLAlchemy entities. 
        ''' 
        
        docs = list(self.__convert_mapped(entities))
        self.add_docs(docs, **kwargs)

    def add_docs(self, docs, **kwargs):
        '''
        Add/update iterable of documents (dictionaries). 
        '''
        commit = not self.transaction
        self._solr.add(docs, commit=commit, **kwargs) 

    def delete(self, ids):
        ''' 
        Delete documents with given ids. ids is a list of node identifiers.
        If id does not exist then it is ignored (no exception is thrown).
        '''
        if ids:
            # Delete in small batches, too many and we get booleanclause errors,
            # too few and it takes too long!
            for ids_chunk in misc.chunker(ids, 20):
                q = 'id:(%s)' % ' '.join('"%s"' % id_ for id_ in ids_chunk) 
                self._solr.delete(q=q, commit=False)
            if not self.transaction:
                self._solr.commit()

