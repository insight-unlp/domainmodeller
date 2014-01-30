'''
Imports data from an IDataConnector.

==============================================================================
Out
==============================================================================

::

    Paper = {
        domain_model   # name of domain model file to use
        url_public     # publicly available url
        url_private    # url to use for text extraction, usually just a filename
                       # (base url can then be specified during TextExtractionStep)
        ...
    }

==============================================================================
Algorithm
==============================================================================

See :DataImportStep.validate_imported for an idea of the expected input format. 

'''

from domainmodeller.storage.schema import Paper
from domainmodeller.task_logger import task_logger

from .IStep import IStep
from domainmodeller.util import misc
from domainmodeller.storage import storage_utils

class DataImportStep(IStep):

    def run(self, s, data_connector):
        papers = data_connector.get_resources()
        
        task_logger.info('Adding %d papers' % (len(papers)))
        self.make_docs(s, papers)
    
    def make_docs(self, s, papers):
        docs = self.doc_iterator(papers)
        for paper_chunk in misc.chunker(docs, 100):
            storage_utils.bulk_insert(s, Paper, paper_chunk)
        
    def doc_iterator(self, papers):
        for paper in papers:
            paper['flag_text_extraction_ok'] = bool(paper.get('raw_text', False))
            yield paper
        
