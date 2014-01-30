from domainmodeller.task_logger import task_logger
import os

SHOW_MEMORY_USAGE = True

#http://fa.bianp.net/blog/2013/different-ways-to-get-memory-consumption-or-lessons-learned-from-memory_profiler/
def memory_usage_psutil():
    # return the memory usage in MB
    try:
        import psutil
    except ImportError:
        return None
    process = psutil.Process(os.getpid())
    mem = process.get_memory_info()[0] / float(2 ** 20)
    return mem
    
class IStep(object):
    def run(self, storage, **kwargs):
        '''Runs the step.'''
        raise NotImplementedError('implement me')

    
    def log_progress(self, num_processed, num_total, word='', message=''):
        if num_total is None or num_total == 0:
            msg = '%s %s processed' % (num_processed, word)
            if message:
                msg += ': %s' % message
        else: 
            progress_bar = self.__make_progress_bar(num_processed, num_total)
            msg = '%s %s processed' % (progress_bar, word)
            if message:
                msg += ' - ' + message
        if SHOW_MEMORY_USAGE:
            mem = memory_usage_psutil()
            if mem:
                msg = 'Mem: %.2fMB - %s' % (mem, msg)
            
        task_logger.info(msg)

    def __make_progress_bar(self, numerator, denominator, width=10, show_percent=True, show_fraction=True):
        '''progress is a floating point number between 0 and 1'''
        progress = float(numerator)/denominator
        dots = '.' * int(progress*width)
        spaces = ' ' * (width - len(dots))
        bar = '[' + dots + spaces + ']'
        if show_percent:
            bar += ' %d' % (progress*100) + '%'
        if show_fraction:
            bar += ' %d/%d' %  (numerator, denominator)
        return bar
