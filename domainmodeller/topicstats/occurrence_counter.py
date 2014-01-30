from domainmodeller.util import nlp_util
from domainmodeller.topicstats.topicstats import WordTrie
import collections

def build_term_trie(paper_terms, tokenizer):
    trie = WordTrie()
    for pt in paper_terms:
        tokens = list(tokenizer(pt.term_string, chars=False))
        trie.add(tokens, pt.topic_slug)
    return trie    

class TermOccurrence:
    def __init__(self, topic_slug, term_string, start, end):
        self.topic_slug = topic_slug
        self.term_string = term_string
        self.start = start
        self.end = end
    
def find_trie_terms(trie, span_tokenizer, paper_text):
    '''Tokenize the paper text and find terms that are in the trie. 
    Returns TermOccurrence objects.'''
    paper_tokens = span_tokenizer(paper_text, chars=True)
    for topic_slug, start_offset, end_offset in trie.find_span_terms(paper_tokens):
        term_string = nlp_util.normalize_spaces(paper_text[start_offset:end_offset])
        yield TermOccurrence(topic_slug, term_string, start_offset, end_offset)

def count_occurrences(term_occurrences):
    '''Given a list of TermOccurrence objects, returns dictionary of 
    {(topic_slug, term_string): (occurrences, unembedded_occ)}
    
    Finds unembedded occurrences by using an algorithm adapted from MPTT tree traversal,
    because having the start and end offset gives us a similar structure to MPTT trees.
    Uncomment the print statement to see the tree output.'''
    occs = collections.defaultdict(lambda: [0,0])
    
    stack = []
    mptt_sorted_occ = sorted(term_occurrences, key=lambda k:(k.start,-k.end))
    for term_occ in mptt_sorted_occ:
        while stack and stack[-1] < term_occ.end:
            del stack[-1]
        depth = len(stack)

        identifier = (term_occ.topic_slug, term_occ.term_string)        

        occs[identifier][0] += 1
        
        # If at 0 depth in trie, the term is not embedded in any other term.
        if not depth:
            occs[identifier][1] += 1
            
        stack.append(term_occ.end)
        
        #For debugging the MPTT structure:
        #print '  '*depth, start, end, term_string, '(%s)'%topic_slug
        
    return occs
