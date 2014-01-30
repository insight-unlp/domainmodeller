import requests
import json
from domainmodeller.util import misc 

def _chunk(return_type, chunk_size):
    '''
    Decorator for a function which takes a single iterable argument.
    Calls the function with iterable in chunks of `chunk_size` and returns
    the aggregated result.

    Reason for existing: DBPedia has an upper limit to the number of results it
    will return for any query. Having separate methods for each was killing
    readability.
    '''
    def wrapper1(fn):
        def wrapper(self, resources, **kwargs):
            result = return_type()
            if return_type==list: 
                method = result.extend
            elif return_type in (set, dict):
                method = result.update
            else: raise ValueError('Invalid type for chunking: %s' % return_type)

            for chunk in misc.chunker(resources, chunk_size):
                method(fn(self, chunk, **kwargs))
            return result
        return wrapper
    return wrapper1
        

_DBPEDIA_RESULT_LIMIT = 1000
class DBPediaUtils:
    '''
    Utilities for querying DBPedia. For each function, `resources` parameter is an
    iterable of dbpedia resources,
    either in local form (e.g. `Natural_language_processing`) or IRI form
    e.g. `http://dbpedia.org/resource/Natural_language_processing`.
    
    For functions with `titles_only` parameter, if `titles_only==True` (default)
    then only local names are returned, otherwise IRI is returned.
    
    Functions are designed to not be limited by the DBPedia maximum query result
    limit (2000 at time of writing).
    '''
    
    _Q_ARTICLES = '''
        select ?resource ?abstract ?comment where {
          values ?resource { %s }
          OPTIONAL {
              ?resource dbpedia-owl:abstract ?abstract . filter (lang(?abstract)='en')
          } 
          OPTIONAL {
              ?resource rdfs:comment ?comment . filter (lang(?comment)='en') .
          }
        }'''
    _Q_DISAMBIGUATED = '''
        select distinct ?page where {
            { values ?page { %s }
              ?page dbpedia-owl:wikiPageDisambiguates [].
            } UNION {
                values ?page { %s }
                ?s dbpedia-owl:wikiPageRedirects ?page .
                filter(strends(str(?s), '(disambiguation)'))
            }
        }'''
    _Q_REDIRECTS = '''
        select ?page ?redirect where {
          VALUES ?page { %s }
          ?page dbpedia-owl:wikiPageRedirects ?redirect.
        }'''

    @_chunk(set, _DBPEDIA_RESULT_LIMIT)    
    def find_disambiguation_pages(self, resources, titles_only=True):
        '''Returns set of all pages which are disambiguation pages.''' 
        resource_values = self._resource_values(resources)
        results = self._query(self._Q_DISAMBIGUATED % (resource_values, resource_values))
        return set(self._get(r,'page',titles_only) for r in results)

    @_chunk(dict, _DBPEDIA_RESULT_LIMIT)
    def find_redirect_pages(self, resources, titles_only=True):
        '''Returns dict of {resource: redirect_resource}+ 
        for resources which redirect to another page.'''
        results = self._query(self._Q_REDIRECTS % self._resource_values(resources))
        ret = {}
        for r in results:
            ret[self._get(r,'page',titles_only)] = self._get(r,'redirect',titles_only)
        return ret

    @_chunk(list, _DBPEDIA_RESULT_LIMIT)
    def fetch_articles(self, resources):
        '''returns dict with keys 
        'dbpedia_url', 'article_abstract', 'article_comment' '''
        
        results = self._query(self._Q_ARTICLES % self._resource_values(resources))

        result_map = [{
            'dbpedia_url': self.__get_value(r, 'resource', required=True),
            'article_abstract': self.__get_value(r, 'abstract'),
            'article_comment': self.__get_value(r, 'comment')
        } for r in results]
        return result_map

    def __get_value(self, data, name, required=False):
        if name in data:
            return data[name]['value'].decode('unicode-escape')
        elif required:
            raise ValueError('"%s" is not in data' % name)
        return None

    def _resource_values(self, resources):
        '''format list of resources for values list, 
        auto detecting if IRI or local name'''
        def url_gen(res):
            for r in res:
                if r.startswith('http:'):
                    yield '<%s>' % r
                else:
                    yield '<http://dbpedia.org/resource/%s>' % r
        return ' '.join(url_gen(resources))
    
    def _get(self, result, variable, title_only):
        val = result[variable]['value']
        if title_only:
            val = val[len('http://dbpedia.org/resource/'):]
        return val
    
    def _query(self, sparql):
        params = {
            'default-graph-uri': 'http://dbpedia.org',
            'query': sparql,
            'format': 'application/sparql-results+json',
            'save': 'display',
            'fname': ''
        }
        rq = requests.post('http://dbpedia.org/sparql', data=params)
        if rq.status_code != 200:
            raise EnvironmentError('Unexpected server response (HTTP code %d): %s' 
                                   % (rq.status_code, rq.text))
        
        # Prevent JSON decoder from interpreting escaped unicode
        content = rq.content.replace('\\U','\\\\U').replace('\\u','\\\\u')
        return json.loads(content)['results']['bindings']

