import logging
from logging import Formatter

class LevelFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno <= self.__level

def _add_handler(logger, msg, min_level, max_level):
    sh = logging.StreamHandler()
    sh.setLevel(min_level)
    sh.addFilter(LevelFilter(max_level))
    formatter = Formatter(msg)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return sh


task_logger = logging.getLogger('task_logger')
task_logger.setLevel(logging.INFO)
_add_handler(task_logger, '[domainmodeller] - [%(asctime)s] - [%(levelname)s] - %(name)s - %(message)s', logging.INFO, logging.INFO)
_add_handler(task_logger, '[domainmodeller] - [%(asctime)s] - [%(levelname)s] - %(name)s - %(message)s', logging.WARN, logging.ERROR)
