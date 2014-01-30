import logging

def init_logger(name, file=None, file_level=logging.INFO,
                console=False, console_level=logging.INFO):

    logger = logging.getLogger(name)
    logger.setLevel(min(file_level, console_level))
    
    if file:
        fmt = '[domainmodeller] - [%(asctime)s] - [%(levelname)s] - %(name)s - %(message)s' 
        sh = logging.FileHandler(file)
        sh.setLevel(file_level)
        sh.setFormatter(logging.Formatter(fmt))
        logger.addHandler(sh)
    
    if console:
        fmt = '[domainmodeller] - [%(asctime)s] - [%(levelname)s] - %(name)s - %(message)s'
        sh = logging.StreamHandler()
        sh.setLevel(console_level)
        sh.setFormatter(logging.Formatter(fmt))
        logger.addHandler(sh)

    return logger