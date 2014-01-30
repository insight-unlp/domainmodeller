'''This step extract terms from text of some limited number of papers that
have not been processed before. Extraction task is distributed using celery.

Definitions: A "term" is a case-sensitive string extracted from the term extractor.
A topic is a collection of terms that all belong to the same morphological root.
E.g. "part-of-speech tagger" and "Part of Speech Taggers" are two term strings
that both belong to the same topic with id "part_of_speech_tagger". 

==============================================================================
In
==============================================================================

::

    Paper = {
        raw_text    # created by TextExtractionStep
        flag_text_extraction_ok=True
        flag_text_extraction_failed=False
    }
    
==============================================================================
Out
==============================================================================

::

    PaperTerm = {
        paper_id
        term_string
        topic_slug       # lemmatized root of the term string. different
                         # morphological variations will have the same root.        
        matches          # Number of times the term extractor detected the term 
                           for this paper
        pattern          # part-of-speech tag sequence (string)
        acronym          # acronym for term if it was detected by the term extractor
    }
    
    Paper {
        flag_term_extraction_ok=True 
    }

'''

from .IStep import IStep
from domainmodeller.celerytasks.celery_tasks import extract_terms
from domainmodeller.task_logger import task_logger
from domainmodeller.termextraction.domain_models import get_model
from domainmodeller.celerytasks.celery_utils import CeleryAsyncRunner
from domainmodeller.storage.schema import PaperTerm, Paper, column_size
from domainmodeller.util import nlp_util
from itertools import groupby

class TermExtractionStep(IStep):
    def run(self, s, num_papers, generate_variations=True):
        papers = s.query(Paper).filter(
                Paper.flag_text_extraction_ok==True,
                Paper.flag_term_extraction_ok==False,
                Paper.flag_text_extraction_failed==False,
        )
        paper_count = papers.count()

        num_papers = min(num_papers, paper_count) if num_papers else paper_count
        if num_papers == 0:
            task_logger.info('No unprocessed papers. Run extract_text first?')
            return

        papers = papers.yield_per(10) # Stream papers
        tasks = TermExtractionCeleryRunner().run(papers, generate_variations)
        paper_pts = self.extract_terms(tasks)
        
        for i, paper, paper_terms in paper_pts:
            s.add_all(paper_terms)
            s.add(paper)
            
            self.log_progress(i, num_papers, message=paper.title, word='papers')
            if (i+1)%100==0:
                s.commit()
    
    def extract_terms(self, tasks):
        num_extracted = 0
        for succeeded, paper, extracted_terms in tasks:
            num_extracted += 1

            if succeeded:
                paper.flag_term_extraction_ok = True
                
                paper_terms = list(self.make_paper_terms(paper, extracted_terms))
                paper_terms = self.merge_paper_terms(paper_terms)
                
                yield num_extracted, paper, paper_terms
            else:
                error_msg = extracted_terms
                task_logger.error('Term extraction failed (%s): %s'
                                   % (paper.id, error_msg))


    def make_paper_terms(self, paper, extracted_terms):
        for extracted_term in extracted_terms:
            #OCR errors in PDFs occasionally lead to no spaces between words
            #and very long topics
            slug = nlp_util.make_topic_slug(extracted_term['term_string'])
            if any(len(word)>40 for word in slug.split('_')):
                continue
            
            # Term extractor occassionally picks up acronyms that aren't acronyms.
            # If they don't fit in the database, remove them to avoid errors.
            acronym = extracted_term.get('acronym')
            if acronym:
                if len(acronym) > column_size(PaperTerm.acronym):
                    acronym = None
            
            paper_term = PaperTerm(
                paper_id = paper.id,
                term_string = extracted_term['term_string'],
                topic_slug = slug,
                matches = extracted_term['matches'],
                pattern = extracted_term['pattern'],
                acronym = acronym,
            )
            yield paper_term
    
    def merge_paper_terms(self, paper_terms):
        # GATE output very occasionally has two of the same term,
        # so need to merge them here as a workaround.
        merged = []
        
        extracted_terms = sorted(paper_terms, key=lambda k: k.term_string)
        grouped = groupby(extracted_terms, key=lambda k: k.term_string)
        for _, group in grouped:
            paper_terms = list(group)
            
            pt = paper_terms.pop(0)
            for other_pt in paper_terms:
                pt.matches += other_pt.matches
                if not pt.acronym and other_pt.acronym:
                    pt.acronym = other_pt.acronym
            
            merged.append(pt)
        
        return merged    


class TermExtractionCeleryRunner:
    def run(self, papers, generate_variations):
        task_gen = self.task_generator(papers, generate_variations)
        return CeleryAsyncRunner(task_gen)

    def task_generator(self, papers, generate_variations):
        for paper in papers:
            domain_model = self.get_domain_model(paper, generate_variations)
            task = extract_terms.delay(paper.raw_text, domain_model)
            yield paper, task
    
    def get_domain_model(self, document, generate_variations):
        model = document.domain_model if document.domain_model else 'default'
        return get_model(model, generate_variations)
