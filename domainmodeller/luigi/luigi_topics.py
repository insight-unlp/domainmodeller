from domainmodeller.util import misc

# Add the client.cfg in the project root,
# because current working directory may be different
client_cfg_path = misc.get_package_path('client.cfg')
from luigi.configuration import LuigiConfigParser
LuigiConfigParser.add_config_path(client_cfg_path)
import luigi.hadoop

import collections
import logging
log = logging.getLogger(__name__)

def topic_num_words(topic_slug):
    return topic_slug.count('_') + 1

class TopicCreationWorkFlow(object):
    
    def __init__(self, use_hadoop, hadoop_path=None, local_scheduler=True):
        self.use_hadoop = use_hadoop
        if use_hadoop:
            # Add Python dependencies to be pickled when running Hadoop jobs
            luigi.hadoop.attach(misc)
        self.hadoop_path = hadoop_path
        self.local_scheduler = local_scheduler
    
    def _init_task(self, task, requires=None):
        task.use_hadoop = self.use_hadoop
        if requires:
            task.set_requires(requires)
        return task
    
    def create_tasks(self, min_unembedded_occ):
        from time import time
        id_ = 'task_' +str(time())
        
        self.pt_dump = self._init_task(DumpData(id_))

        self.topics_task = self._init_task(ProcessTopics(id_, min_unembedded_occ), 
                                           requires=self.pt_dump)
        self.pref_string = self._init_task(PreferredStringCalc(id_, min_unembedded_occ), 
                                           requires=self.pt_dump)
        
    def dump_paper_term_data(self, data_tuples):
        self.pt_dump.data_tuples = data_tuples
        self.pt_dump.run()
        # Unset to prevent it getting pickled when sending to Hadoop
        self.pt_dump.data_tuples = None
        
    def process_topics(self):
        task = self.topics_task
        luigi.build([task], local_scheduler=self.local_scheduler)
        return task.iterate_output()

    def calc_pref_string(self):
        task = self.pref_string
        luigi.build([task], local_scheduler=self.local_scheduler)
        return task.iterate_output()
    
    def cleanup(self):
        '''Delete output files'''
        self.pt_dump.cleanup()
        self.topics_task.cleanup()
        self.pref_string.cleanup()

class WorkflowTask(luigi.Task):
    id = luigi.Parameter()
    __requires = []

    def output(self):
        filename = "%s_%s" % (self.id, self.__class__.__name__) 
        return luigi.LocalTarget(misc.temporary_file_path(filename))

    def set_requires(self, requires):
        self.__requires = requires
    
    def requires(self):
        return self.__requires
    
    def cleanup(self):
        try:
            self.output.remove()
        except Exception as e:
            log.warn("Failed to delete output: %s" % e)
            return False

class IterableMRTask(luigi.hadoop.JobTask):
    '''For iterating the output of a mapreduce task without all the unreadable tuple
    indexes and type conversion. Subclasses define the fields and types that are in 
    the output file, e.g. `output_fields = [('word', unicode), ('count', int)].
    
    Calling iterate_output then returns a generator which yields named tuples, e.g.
    
    ::
    
      for row in mytask.iterate_output():
          print row.word, row.count
    '''

    use_hadoop = False

    def output(self):
        filename = "%s_%s" % (self.id, self.__class__.__name__) 
        if self.use_hadoop:
            # Output format must be PlainDir so luigi will look for part-* files
            # in iterate_output()
            return luigi.hdfs.HdfsTarget(filename, format=luigi.hdfs.PlainDir)
        else:
            return luigi.LocalTarget(misc.temporary_file_path(filename))
    
    output_fields = NotImplemented

    def iterate_output(self):
        tuple_keys = [k[0] for k in self.output_fields]
        key_types = [k[1] for k in self.output_fields]

        nt = collections.namedtuple(self.__class__.__name__, tuple_keys)
        
        with self.output().open('r') as f:
            for line in f:
                fields = line.decode('utf-8').split('\t')
                # Remove \n from last field
                fields[-1] = fields[-1].rstrip('\n')
                # Convert types
                fields = [f(fld) for f, fld in zip(key_types, fields)]
                yield nt(*fields)


class DumpData(WorkflowTask):
    '''Write tuples of data to tab-separated files on the filesystem for processing.
    Copies files to HDFS after completion if use_hadoop=True. Assumes data do not have tab
    values in them already.'''
    use_hadoop = False
    data_tuples = None

    hdfs_path = None
    def copy_to_hdfs(self):
        from luigi.hdfs import client, tmppath
        local_path = self.output().path
        hdfs_path = tmppath()
        client.copy(local_path, hdfs_path)
        self.hdfs_path = hdfs_path
    
    def output(self):
        if not self.hdfs_path:
            return super(DumpData, self).output()
        else:
            return luigi.hdfs.HdfsTarget(self.hdfs_path)

    def run(self):
        with self.output().open('w') as f:
            for data_tuple in self.data_tuples:
                stringified = [unicode(d) if d is not None else '' for d in data_tuple]
                print >> f, '\t'.join(stringified).encode('utf-8')
            
        if self.use_hadoop:
            self.copy_to_hdfs()


class ProcessTopics(IterableMRTask, WorkflowTask):
    min_unembedded_occ = luigi.IntParameter()
    
    output_fields = [('slug', unicode), ('occurrences', int), ('matches', int),
                     ('paper_count', int), ('word_count', int), ('acronym', unicode)]
    
    def mapper(self, pt):
        paper_id, topic_slug, _, matches, occ, unembedded_occ, acronym = pt.split('\t')
        yield topic_slug, (paper_id, int(matches), int(occ), int(unembedded_occ), acronym)
    
    def reducer(self, topic_slug, vals):
        num_words = topic_num_words(topic_slug)
        
        t_occ = 0
        t_matches = 0
        t_unembedded_occ = 0
        t_acronym = ''
        paper_ids = set()

        for paper_id, matches, occurrences, unembedded_occ, acronym in vals:
            t_matches += matches
            t_occ += occurrences
            t_unembedded_occ += unembedded_occ  
            paper_ids.add(paper_id)
            if acronym:
                t_acronym = acronym

        if t_unembedded_occ >= self.min_unembedded_occ:
            yield topic_slug, (t_occ, t_matches, len(paper_ids), num_words, t_acronym)

### Preferred string calculation

class PreferredStringCalc(IterableMRTask, WorkflowTask):
    '''Pick the maximum occurring string for each topic slug'''
    output_fields = [('slug', unicode), ('pref_string', unicode)]
    min_unembedded_occ = luigi.IntParameter()
        
    def mapper(self, pt):
        _, topic_slug, term_string, _, occurrences, _, _ = pt.split('\t')
        yield topic_slug, (term_string, int(occurrences))

    def reducer(self, topic_slug, term_occs):
        # Optimisation: Most terms will only have one occurrence. 
        # We can reduce the output size of this task by filtering on minimum unembedded
        # occurrences.
        count = collections.defaultdict(int)
        for term_string, occurrences in term_occs:
            count[term_string] += occurrences
        if sum(count.itervalues()) >= self.min_unembedded_occ:
            yield topic_slug, max(count, key=lambda k:count[k])

