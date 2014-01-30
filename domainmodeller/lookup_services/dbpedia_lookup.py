import pysolr
import re

class DBPediaTitleLookup():
    '''
    Query a Solr index of DBPedia titles. See scripts/dbpedialookup
    '''
    def __init__(self, host):
        self.s = pysolr.Solr(host)
    
    def __query(self, title, field):
        n = len(re.findall(r'[^-\s]+', title))
        title = title.replace('"', '')
        q = '%s:"%s" AND n:%d' % (field, title, n)
        response = self.s.search(q, limit=10000)
    
        return [r['title'] for r in response.docs]
    
    def query_exact(self, title):
        return self.__query(title, 'title')
    
    def query_minimal_stem(self, title):
        return self.__query(title, 'minimal_stem')
        
if __name__=='__main__':
    import sys
    from domainmodeller.settings import DBPEDIA_LOOKUP_SERVICE
    service = DBPediaTitleLookup(DBPEDIA_LOOKUP_SERVICE)
    
    print service.query_minimal_stem(' '.join(sys.argv[1:]))
    