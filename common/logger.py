import logging
import sys


def setup_logger(filename: str = None, level=logging.INFO):
    if filename:
        handler = logging.FileHandler(filename, mode='w', encoding='utf-8')
    else:
        handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter('%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(handler)
