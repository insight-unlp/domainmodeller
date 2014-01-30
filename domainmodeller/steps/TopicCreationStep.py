'''
This step creates topics from extracted terms, counting occurrences
and basic statistics.

==============================================================================
IN
==============================================================================

::

    Paper = {
        raw_text
        flag_term_extraction_ok=True
    }
    
    PaperTerm = {
        #Output of TermExtractionStep
    }


==============================================================================
OUT
==============================================================================

::

    # a topic is created for a set of terms with the same term_root
    Topic = {
        slug             # Lemmatized, lowercase, URL-friendly ID e.g. "machine_learning"
        topic_string     # preferred term string (max occurrences)
        word_count       # Number of words in topic (used for ranking algorithms)
                
        matches          # a sum of matches of all morphological variations
        occurrences      # sum of occurrences of all morphological variations across the 
                           corpus.
                        
        paper_count      # number of papers in which the topic occurs
        acronym
    }


==============================================================================
ALGORITHM
==============================================================================

Uses the Luigi library to batch process topics in a MapReduce workflow.
This is a batch task for now... doing this incrementally is quite tricky.

1. Build a WordTrie of all term strings discovered by the term extractor (from
       PaperTerm objects).
2. Count occurrences of all terms in the corpus, and dump to filesystem or HDFS.
   We don't put the occurrences in PaperTerm because we only need them as an intermediate
   step (i.e. no point in putting them into the database just to dump them to a file)
3. Run MapReduce tasks to merge the data from step 2 into Topic/PaperTopic objects

==============================================================================
Future work
==============================================================================

Scaling out
-----------

- Run the occurrence counter in a MapReduce workflow:
  - Would require implementing a one-file-per-mapper workflow in Luigi
  - Would need to do a join (Hive) with existing paper terms after, we need a
    way to make a Hive dependency optional.

- Distributed WordTrie implementation (though only need this kind of scaling for huge
  datasets).


- Incremental addition/deletion of papers

'''

import logging

from IStep import IStep
from domainmodeller.luigi import luigi_topics
from domainmodeller.storage import storage_utils
from domainmodeller.storage.schema import Paper, Topic, PaperTerm
from domainmodeller.storage.storage_utils import reset_tables
from domainmodeller.task_logger import task_logger
from domainmodeller.topicstats.occurrence_counter import find_trie_terms, count_occurrences, \
    build_term_trie
from domainmodeller.util import nlp_util
from domainmodeller.util.misc import enum_chunker
from domainmodeller.util.nlp_util import topic_occ_tokenizer
from sqlalchemy.sql.functions import func

log = logging.getLogger(__name__)

class TopicCreationStep(IStep):

    def reset(self, s):
        log.info("Deleting Topic tables...")
        reset_tables(s, Topic)
        s.commit()

    def count_term_corpus_occs(self, s, num_papers):
        processed = 0
        for paper_id, term_occs in count_pt_occ_all(s):
            existing_pts = s.query(PaperTerm).filter(PaperTerm.paper_id==paper_id)
            for line in merge_and_flatten_pts(paper_id, term_occs, existing_pts):
                yield line
            
            processed += 1
            if processed%100 == 0:
                self.log_progress(processed, num_papers, 'papers')

    def run(self, s, min_occ, use_hadoop, hadoop_path=None):
        self.reset(s)
        num_papers = s.query(func.count(Paper.id)).filter(
                        Paper.flag_term_extraction_ok==True,
                    ).scalar()
        
        workflow = luigi_topics.TopicCreationWorkFlow(use_hadoop=use_hadoop, 
                                    local_scheduler=True)
        try:
            workflow.create_tasks(min_occ)
            data_tuples = self.count_term_corpus_occs(s, num_papers)
            workflow.dump_paper_term_data(data_tuples)
            
            task_logger.info('Creating topics')
            topic_gen = self.create_topics(s, workflow)
            for i, topics in enum_chunker(topic_gen):
                storage_utils.bulk_insert(s, Topic, topics)
                self.log_progress(i, None, 'topics')
            
        finally:
            workflow.cleanup()

    def create_topics(self, s, workflow):
        '''Returns dict of {slug: topic_id}'''
        pref_strings = {slug: self.prettify_topic_string(pref_string) 
                        for slug, pref_string in workflow.calc_pref_string()}
        for i, t in enumerate(workflow.process_topics()):
            # Optimisation: Use dicts to allow bulk inserts
            topic = dict(
                id = i+1,
                topic_string = pref_strings[t.slug],
                slug = t.slug,
                occurrences = t.occurrences,
                matches = t.matches,
                paper_count = t.paper_count,
                acronym = t.acronym or None,
                word_count = t.word_count
            )
            yield topic
    
    def prettify_topic_string(self, preferred):
        words = nlp_util.split_words(preferred)
        # If string is uppercase and has more than one word, it probably shouldn't
        # by uppercase 
        if len(words) > 1 and preferred.isupper():
            return preferred.capitalize()
        
        # Make first letter of first word uppercase unless word has unusual capitalisation
        if words[0].islower():
            return preferred.capitalize()
        return preferred


def term_filter(paper_terms):
    for pt in paper_terms:
        if nlp_util.is_compound_phrase(pt.term_string):
            continue
        yield pt

def count_pt_occ_all(s):
    '''
    To allow processing multiple conferences from different domains within one database,
    we build an occurrence counter trie for each conference, so that terms from
    different conferences aren't searched for in other conferences.
    '''
    tokenizer = topic_occ_tokenizer()
    # Paper objects are large, stream them in smaller chunks
    papers = s.query(Paper).filter(Paper.flag_term_extraction_ok==True).yield_per(100)
    paper_terms = s.query(PaperTerm).yield_per(10000)
    for result in count_pt_occ(s, tokenizer, papers, paper_terms):
        yield result
    

def count_pt_occ(s, tokenizer, papers, paper_terms):
    '''
    Build a trie of terms discovered by the term extractor and counts occurrences
    of those terms in the corpus.
    Also counts occurrences where a term is found in another document but was not matched
    in that document.
    
    1,000,000 unique term strings ~= 50mb so this should always fit in memory. If needed 
    to scale beyond this in the future, it should be possible to implement the word 
    trie in a database (higher latency but scalable throughput).
    '''

    task_logger.info("Building term trie")
    filtered_pts = term_filter(paper_terms)
    trie = build_term_trie(filtered_pts, tokenizer)
    task_logger.info("Finished building term trie")
    for paper in papers:
        trie_occurrences = list(find_trie_terms(trie, tokenizer, paper.raw_text))
        term_occurrences = count_occurrences(trie_occurrences)
        yield paper.id, term_occurrences

def merge_and_flatten_pts(paper_id, term_occurrences, existing_pts):
    '''Merge found occurrences with existing PaperTerms (for use with Luigi). 
    Yields tuples for writing to CSV'''
    existing_by_term = {pt.term_string: pt for pt in existing_pts}
    
    items = term_occurrences.iteritems()
    for (topic_slug, term_string), (occurrences, unembedded_occs) in items:
        matches = 0
        acronym = None
        if term_string in existing_by_term:
            matches = existing_by_term[term_string].matches
            acronym = existing_by_term[term_string].acronym
        
        # Note: Although we count unembedded occurrences here, it is only
        # for better filtering by minimum occurrences. It is recalculated
        # in TopicStatsStep because the values can be significantly different
        # after filtering topics.
        yield (paper_id, topic_slug, term_string, matches, 
               occurrences, unembedded_occs, acronym)
