'''
Tools for computing statistics for topics.
@author Barry Coughlan
'''

import sys
from domainmodeller.util import nlp_util 
from collections import defaultdict

class WordTrie:
    LEAF = '__LEAF__'
    
    def __init__(self):
        self.trie = {}
    
    def add(self, words, value):
        trie = self.trie
        for word in words:
            if word not in trie:
                trie[word] = {}
            trie = trie[word]
        trie[self.LEAF] = value
    
    def print_trie(self, first_node=None, writer=sys.stdout):
        if first_node:
            self._print_trie(writer, self.trie[first_node], 0)
        else:
            self._print_trie(writer, self.trie, 0)
        writer.write('\n')

    def _print_trie(self, writer, trie, depth):
        if self.LEAF in trie:
            # Print the LEAF value first
            writer.write(':' + str(trie[self.LEAF]))
        for word in trie:
            if word != self.LEAF:
                writer.write("\n%s%s" % ("  "*depth, word))
                self._print_trie(writer, trie[word], depth+1)

    def find_term_occurrences(self, tokens):
        '''tokens can be any iterable, including generator.'''
        terms = defaultdict(int)
        
        searching = [self.trie]
        for token in tokens:
            new_searching = [self.trie]
            for branch in searching:
                if self.LEAF in branch:
                    terms[branch[self.LEAF]] += 1
                if token in branch:
                    new_searching.append(branch[token])
            searching = new_searching
        # Last token
        for t in searching:
            if self.LEAF in t:
                terms[t[self.LEAF]] += 1
        return terms

    def find_span_terms(self, tokens):
        '''Find terms from tokens with span values. Input is a sequence of
        (token, start_offset, end_offset). Finds terms and yields
        (value, start_offset, end_offset).'''
        searching = []
        for token in tokens:
            searching.append((token, self.trie))
            
            new_searching = []
            for start_token, branch in searching:
                if token[0] in branch:
                    new_branch = branch[token[0]]
                    if self.LEAF in new_branch:
                        yield (new_branch[self.LEAF], start_token[1], token[2])
                    new_searching.append((start_token, new_branch))
            searching = new_searching


class EmbeddednessCalculator:
    def __init__(self):
        self.topic_map = {}
        
    def add(self, tokens, topic):
        key = tuple(tokens)
        self.topic_map[key] = topic

    def calculate(self):
        '''
        Iterate over every possible sequence of tokens in each topic, and check
        if that embedded topic exists in the topic map.
        Not as slow as it sounds as topics are usually no more than 5 tokens long.
        '''
        embeddedness_map = defaultdict(list)
        for topic_seq in self.topic_map:
            for key in nlp_util.variable_sliding_window(topic_seq, len(topic_seq)):
                if key in self.topic_map:
                    embedded_topic = self.topic_map[key]
                    embeddedness_map[embedded_topic.id].append(self.topic_map[topic_seq])
        return embeddedness_map
