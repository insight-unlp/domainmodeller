'''
Helper module for fetching domain models with caching support. 
'''

from domainmodeller.util import misc 
try:
    from functools import lru_cache
except:
    from functools32 import lru_cache


def _read_model(name):
    with open(misc.get_package_path('domainmodels', name+'.txt')) as f:
        return [line.strip() for line in f.readlines() if len(line.strip())>0]

def _generate_variations(domain_model):
    '''Generate variations from a list of domain words,
    e.g. generate_variations(['use']) -> ['use', 'uses', 'using', 'used']
    We need to do this because the Java Services term extractor
    will only match exact terms. It doesn't matter if we get some invalid words
    resulting from this, because they won't be matched in the text anyways.'''
    from pattern.text.en import inflect
    
    result = set()
    for word in domain_model:
        variations = inflect.lexeme(word)
        result = result.union(variations)
        
    return sorted(list(result))
        
    
@lru_cache()
def get_model(name, generate_variations):
    model = _read_model(name)
    if generate_variations:
        model = _generate_variations(model)
    return model