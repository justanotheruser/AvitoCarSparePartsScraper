import logging
import sys


def setup_logger(filename: str = None):
    if filename:
        handler = logging.FileHandler(filename, mode='w', encoding='utf-8')
    else:
        handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('[%(levelname)s] [%(threadName)s] %(message)s'))
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
