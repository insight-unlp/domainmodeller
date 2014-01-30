#!/usr/local/bin/python
# coding: utf-8

import time
from domainmodeller.util import misc 
from domainmodeller.task_logger import task_logger
from domainmodeller.util.misc import extract_fn_arguments
import types

__docformat__ = u'restructuredtext en'

from os.path import isfile
from collections import OrderedDict
from domainmodeller import settings
import logging
log = logging.getLogger(__name__)

class TaskError(Exception):
    '''
    TaskError thrown on failure within the task.
    This is to ensure correct exit codes.
    '''
    pass

class CommandLineArgsError(TaskError):
    pass

class TaskHub:
    def __init__(self, storage):
        self.storage = storage
        
        self._task_name_to_func = OrderedDict([
            ('clear_storage',                    self.task_clear_storage),
            ('stats',                            self.task_stats),
			
            ('import_directory',                 self.task_import_directory),
            
            ('extract_terms',                    self.task_extract_terms),
            ('create_topics',                    self.task_create_topics),
            ('dbpedia_lookup',                   self.task_dbpedia_lookup),
            ('topic_stats',                      self.task_topic_stats),
            ('entity_classes',                   self.task_entity_classes),
        ])
        # For printing out titles in the command line.
        self._groups = {
            'clear_storage': 'Utilities',
            'import_directory': 'Data Import',
            'extract_terms': 'Topic steps',
        }


    def _parse_string_args(self, func, params_list):
        fn_args, fn_kwargs = extract_fn_arguments(func, excluded=['self', 'session'])
        
        args, kwargs = [], {}
        
        for parameter in params_list:
            pv = [p.strip() for p in parameter.split('=',1)]
            if len(pv) == 1:
                args.append(pv[0].strip())
            else:
                kwarg, kwval = pv
                
                # If the default kwarg is a boolean, convert string to boolean
                if type(fn_kwargs[kwarg]) == types.BooleanType:
                    if kwval.lower()=='true':
                        kwval = True
                    elif kwval.lower()=='false':
                        kwval = False
                    else:
                        raise ValueError('Argument %s must be True/False' % kwarg)
                kwargs[kwarg] = kwval

        if len(args) != len(fn_args):
            raise CommandLineArgsError('Received %d required arguments, required %d'
                             % (len(args), len(fn_args)))

        return args, kwargs


    def run(self, text_input):
        '''Parses and runs the text_input.'''

        parts = text_input.split()

        task_name = parts.pop(0).strip()

        func = self._task_name_to_func.get(task_name, None)
        if not func:
            task_logger.error('No such task: %s' % task_name)
            return

        args, kwargs = self._parse_string_args(func, parts)
        
        # Run task
        t1 = time.time()
        task_logger.info('[begin] %s\n' % text_input)
        
        try:
            with self.storage.session_scope() as session:
                func(session, *args, **kwargs)
        except Exception as e:
            task_logger.exception(e)
            raise
        
        t2 = time.time()
        msg = '[done] in %.2fs seconds: %s' % (t2-t1, text_input)
        task_logger.info(msg)

    def task_clear_storage(self, session):
        '''Re-initialize the database. Deletes everything. Cannot be undone!'''
        self.storage.clear()

    def task_stats(self, session):
        '''Summary statistics from the database.'''
        from domainmodeller.steps.StatsTask import StatsTask
        StatsTask().run(session)
        
    def task_import_directory(self, session, directory):
        '''
        Import a directory of text files (no authors, only papers). Useful for doing
        only analysis of topics.
        '''
        from domainmodeller.steps.DataImportStep import DataImportStep
        from domainmodeller.dataconnectors.DirectoryDataConnector import DirectoryDataConnector
        
        task_logger.info('Importing files in %s' % directory)

        data_connector = DirectoryDataConnector(directory)
        DataImportStep().run(session, data_connector)

        
    def task_extract_terms(self, session, num_papers=None, generate_variations=True):
        '''
        Extract terms from text. Depends on extract_text.
        generate_variations generates word variations from the domain model,
        e.g. use -> uses, using, used. This is generally a good idea, as the
        Java term extractor will only find exact domain model words.
        '''
        from domainmodeller.steps.TermExtractionStep import TermExtractionStep

        TermExtractionStep().run(session, 
                                 num_papers=int(num_papers) if num_papers != None else None,
                                 generate_variations=generate_variations)
    
    def task_create_topics(self, session, min_occ=1,
                           use_hadoop=settings.LUIGI_USE_HADOOP):
        '''
        Consolidate extracted terms into 'topics', and computes some basic metrics, e.g.
        number of occurrences of topic variations across the corpus. Only term roots with
        at least min_words words are considered. A topic must have at least min_occ
        occurrences across the whole corpus to be considered.
        '''
        from domainmodeller.steps.TopicCreationStep import TopicCreationStep
        TopicCreationStep().run(session, int(min_occ), use_hadoop)

    def task_topic_stats(self, session, min_score=0):
        '''
        Rank and score topics and paper-topic relations. Topics with scores below min_score
        will be filtered. Embeddedness is the number of topics of which a topic is a
        substring. If loose_embeddedness is True, then the topic's words can appear in any
        order.
        '''
        
        from domainmodeller.steps.TopicStatsStep import TopicStatsStep
        
        TopicStatsStep().run(session, float(min_score))

    def task_dbpedia_lookup(self, session, num_topics=None, reset_all=False):
        '''Link topics to DBPedia resources If num_topics is not specified, will attempt 
        to match all topics. If reset_all=True, any previous matches will be reset
        (i.e. for re-processing the whole dataset).'''
        from domainmodeller.steps.DBPediaLookupStep import DBPediaLookupStep
        DBPediaLookupStep().run(session, 
                                settings.DBPEDIA_LOOKUP_SERVICE,
                                int(num_topics) if num_topics!=None else None,
                                reset_all=reset_all)


    def task_entity_classes(self, session):
        '''Extract entity classes and print to stdout (for EuroSentiment project).'''
        from domainmodeller.steps.EntityClassTask import EntityClassTask
        EntityClassTask().run(session)

