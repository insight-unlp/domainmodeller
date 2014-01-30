from celery.result import ResultSet
from celery import states
from Queue import Queue

import logging
log = logging.getLogger(__name__)

__all__=['CeleryAsyncRunner']

class CeleryAsyncRunner:
    '''
    Celery asynchronous task runner, limits maximum number by running tasks in batches,
    to reduce memory usage in the case that there are thousands of tasks.
    
    Make celery more friendly for batch processing and unit tests.
    '''

    def __init__(self, task_generator, queue_max=500, loading_factor=0.1):
        '''
        :task_generator generator which yields tuples of (key, task)
        '''
        
        self.task_generator = task_generator
        self.queue_max = queue_max
        # Fill up the queue when it goes below this size
        self.refill_size = int(queue_max*loading_factor)
        self.queue_size = 0
        
        self.task_batches = Queue()
        self._fill_queue()

    def _fill_queue(self):
        identifier_map = {}
        
        async_results = []
        for identifier, task in self.task_generator:
            async_results.append(task)
            identifier_map[task.id] = identifier 
            
            self.queue_size += 1
            if self.queue_size == self.queue_max:
                break

        if async_results:
            log.info("Writing %d tasks to queue" % len(async_results))
            self.task_batches.put( (identifier_map, ResultSet(async_results)) )
    
    def __iter__(self):
        while not self.task_batches.empty():
            identifier_map, result_set = self.task_batches.get()

            for celery_id, task in patched_iter_native(result_set):
                succeeded = (task['status']==states.SUCCESS)
                identifier = identifier_map.pop(celery_id)

                yield succeeded, identifier, task['result']

                # For loop does not finish until ResultSet is exhausted
                # Send some more tasks for processing if the number of tasks
                # in the queue goes below the threshold.
                self.queue_size -= 1
                if self.queue_size <= self.refill_size:
                    log.info("Filling queue, reached threshold size %d" % self.queue_size)
                    self._fill_queue()

def patched_iter_native(result_set):
    '''Workaround for Celery's iter_native which does not work with CELERY_ALWAYS_EAGER. 
    If the results have a backend, return the r of the backend's iter_native,
    otherwise assume they are EagerResults and simulate the output of iter_native.
    
    This is allow Celery to work in "eager" (local, non-distributed) mode, useful
    for unit tests.'''
    
    results = result_set.results
    if not results:
        return iter([])

    if results[0].backend:
        return result_set.iter_native()
    else:
        return ( (r.id, {'status': states.SUCCESS, 'result': r.result}) for r in results )

