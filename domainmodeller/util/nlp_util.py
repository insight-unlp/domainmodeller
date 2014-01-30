'''
Tokenizers, analysers etc.
'''

import re
from functools32 import lru_cache

_RE_WORD_HYPHEN = re.compile(r"[^-\s]+")
_RE_WORD_NO_HYPHEN = re.compile(r"[^\s]+")

def split_words(text, split_hyphens=False):
    regex = _RE_WORD_HYPHEN if split_hyphens else _RE_WORD_NO_HYPHEN
    return regex.findall(text)

def is_special_word(word):
    # e.g. acronym (all uppercase) or unusual capitalization (e.g. jQuery)
    return not word[1:].islower()

def lemmatize(term, split_hyphens=True, delimiter=' '):
    words = split_words(term, split_hyphens=split_hyphens)
    return delimiter.join(lemmatize_word(w) for w in words)

_lemmatizer = None
def lemmatizer():
    # Lazy load lemmatizer because it is slow on import and first use
    global _lemmatizer
    if not _lemmatizer:
        from nltk.stem import WordNetLemmatizer
        _lemmatizer = lru_cache(maxsize=50000)(WordNetLemmatizer().lemmatize)
    return _lemmatizer

def make_topic_slug(term_string):
    '''Use NLTK WordNet stemmer because GATE does not lemmatize words beginning
    with capital letter, leading to separate topics for "Machine learning" and
    "Machine Learning".'''
    return lemmatize(term_string, split_hyphens=True, delimiter='_')

def lemmatize_word(word):
    if is_special_word(word):
        return word.lower()
    else:
        return lemmatizer()(word.lower())

class SimpleRegexTokenizer:
    def __init__(self, split_hyphens=False):
        regex = r"\w+(\.?\w+)*" if split_hyphens else r"[\w-]+(\.?[\w-]+)*"  
        self.regex = re.compile(regex, re.UNICODE)
        
    def __call__(self, text):
        for match in self.regex.finditer(text):
            yield match.group(0)
    
def variable_sliding_window(iterable, max_window_size):
    '''
    yields sliding windows of iterable, up to size max_window_size.
    Be cautious of iterable size, this scales as sum of series (.5*(n**2 + n)).
    '''
    for window_size in xrange(1, min(len(iterable), max_window_size)):
        for window_pos in xrange(0, len(iterable)-window_size+1):
            yield tuple(iterable[window_pos : window_pos+window_size])

def count_words(string, splitter=re.compile(r'\w+')):
    '''Count words in string. Hyphenated words are counted as multiple words
    by default.'''
    return sum(1 for _ in splitter.finditer(string))

def is_compound_phrase(phrase):
    return 'and' in split_words(phrase)[1:-1]

class topic_occ_tokenizer():
    '''
    - Don't tokenize on hyphens.
    - Tokenize punctuation
    '''
    
    def __init__(self):
        self.expression = re.compile(r"((\w+([\.-]?\w+)*)|[\.,;])", re.UNICODE)
    
    def __call__(self, value, chars=True):
        for match in self.expression.finditer(value):
            text = match.group(0).lower()
            if not chars:
                yield text
            else:
                yield (text, match.start(), match.end())

def normalize_spaces(string):
    '''
    >>> normalize_spaces('the  quick\nbrown \nfox\n\njumped')
    'the quick brown fox jumped'
    '''
    return re.sub('\s+', ' ', string)
    
