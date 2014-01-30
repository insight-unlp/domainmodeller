from domainmodeller.TaskHub import TaskHub
from domainmodeller.util.pretty_doc import pretty_doc
from domainmodeller.util import misc
from domainmodeller import logging_utils
import logging

log_path = misc.get_package_path('logs', 'domainmodeller.log')

def run(storage, args, log_console=False, log_level=logging.INFO):
    task_hub = TaskHub(storage)
    
    logging_utils.init_logger('domainmodeller', console=log_console, console_level=log_level, 
                              file=log_path, file_level=log_level)
    logging_utils.init_logger('task_logger', file=log_path, file_level=log_level)
    
    task_name = args[0] if len(args)>0 else None
    if task_name and task_name != 'help' and task_name in task_hub._task_name_to_func:
        task_hub.run(' '.join(args))
    else:
        print('')
        print(pretty_doc(task_hub._task_name_to_func, task_hub._groups,
                         docstrings=(task_name=='help'), exclude_vars={'session'}))
        print('\nRun task with "-v" for verbose output, or "-vv" for very verbose output')
        if task_name != 'help':
            print('**Run "domainmodeller help" to get detailed descriptions of the steps**\n')

def main():
    from domainmodeller import settings
    
    # Parse command line arguments
    from sys import argv

    verbose = '-v' in argv
    if verbose: argv.remove('-v')

    log_level = logging.DEBUG if '-vv' in argv else logging.INFO
    if log_level==logging.DEBUG: argv.remove('-vv')
    
    if '-D' in argv:
        loc = argv.index('-D')
        del argv[loc]
        database = argv[loc]
        del argv[loc]
    else:
        database = settings.DATABASE

    from domainmodeller.storage import Storage
    storage = Storage.init_storage(database, **settings.BACKEND)
    run(storage, argv[1:], log_console=verbose, log_level=log_level)
    
if __name__ == '__main__':
    main()