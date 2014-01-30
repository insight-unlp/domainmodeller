
import logging
import codecs
import os
from os.path import join, splitext
log = logging.getLogger(__name__)


from domainmodeller.dataconnectors.IDataConnector import IDataConnector

def _text(el):
    if el is None:
        return None

    if el.text is None:
        return None
    return el.text.strip()

class DirectoryDataConnector(IDataConnector):
    '''For importing files from a directory (no authors, only papers).'''

    def __init__(self, dataset_folder, file_extensions=None):
        self.dataset_folder = dataset_folder
        if file_extensions:
            self.file_extensions = [fe.lstrip('.') for fe in file_extensions]
        else:
            self.file_extensions = None

    def get_resources(self):
        return self.__papers()
        
    def __valid_extension(self, filename):
        if self.file_extensions:
            return splitext(filename)[1].lstrip('.') in self.file_extensions
        return True

    def __papers(self):
        papers = []
        for root, _, files in os.walk(self.dataset_folder):
            for filename in files:
                if filename.startswith('.') or not self.__valid_extension(filename):
                    continue

                full_filename = join(root, filename)
                paper = self.__make_paper(full_filename)
                papers.append(paper)
            
        return papers

    def __make_paper(self, filename):
        with codecs.open(filename, "r", "utf-8") as f:
            contents = f.read()
            
            basename = os.path.basename(filename)

            return {
                'slug': basename,
                'raw_text': contents,
                'title': basename,
            }
