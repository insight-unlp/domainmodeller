import requests
import logging

log = logging.getLogger(__name__)

class JavaServicesTermExtractor(object):
    '''
    Uses the Java term extraction from which is hosted as a service
    '''

    def __init__(self, server):
        self.server = server
        
    def extract_terms(self, document, domain_model):
        '''
        document: string
        domain_model: list of strings
        '''

        if not document:
            raise ValueError('empty document')
            

        data = {
            'domainModel': domain_model,
            'document': document
        }

        rq = requests.post(self.server+'/api/termextraction', data=data)
        if rq.status_code != 200:
            raise EnvironmentError("Unexpected server response (HTTP code %d): %s" 
                                   % (rq.status_code, rq.text))
        ss_terms = rq.json()
        
        if ss_terms is None:
            # request gives None for empty JSON (no terms extracted), 
            # throws exception if can't parse.
            return []
        
        ss_terms = ss_terms['topic']
        return self.__convert_to_format(ss_terms)
        
    def __convert_to_format(self, ss_terms):
        terms = []
        # JAX-RS doesn't make a list when there's only one occurrence, 
        # so we have to compensate for that
        if isinstance(ss_terms, dict):
            ss_terms = [ss_terms]
        for ss_term in ss_terms:
            mvs = ss_term['morphologicalVariations']
            if isinstance(mvs, dict):
                mvs = [mvs]

            for mv in mvs:
                # Term should not end with an adjective
                if any(mv['pattern'].endswith(p) for p in ['VBN', 'CD', 'VBG', 'JJ']):
                    log.info('Filtering term ending in adjective: %s (%s)'
                             % (mv['pattern'], mv['termString']))
                    continue

                term = {
                    'term_string': mv['termString'],
                    'matches': int(mv['extractedTermOccurrences']),
                    'pattern': mv['pattern'],
                }
                if 'acronym' in mv:
                    term['acronym'] = mv['acronym']
                terms.append(term)

        return terms
