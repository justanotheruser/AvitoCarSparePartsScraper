import json
import logging
import os
import sys
import time

import openpyxl
import pika

sys.path.append(os.path.dirname(__file__) + "/..")
from common.logger import setup_logger
from common.config import read_config
from common.queues import SEARCH_QUERIES_QUEUE


def read_search_queries_from_file(filename: str):
    logging.info(f'Started reading {filename}')
    try:
        wb = openpyxl.load_workbook(filename)
    except Exception as e:
        logging.error(e)
        return
    sheet = wb.active
    logging.debug(sheet)
    for i, row in enumerate(sheet.iter_rows(values_only=True)):
        if i == 0:
            continue
        yield {'car_brand': row[0], 'car_model': row[1], 'spare_part': row[2]}


def main():
    setup_logger('input_reader.log', level=logging.INFO)
    cfg = read_config()
    if not cfg:
        return

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=SEARCH_QUERIES_QUEUE)

    for i, query in enumerate(read_search_queries_from_file(cfg.input.file)):
        logging.debug(query)
        if i % 10_000 == 0:
            res = channel.queue_declare(queue=SEARCH_QUERIES_QUEUE, passive=True)
            queue_size = res.method.message_count
            while queue_size >= 10_000:
                logging.info(f'Size of {SEARCH_QUERIES_QUEUE} queue is {queue_size}, pausing for now...')
                time.sleep(10)
        channel.basic_publish(exchange='',
                              routing_key=SEARCH_QUERIES_QUEUE,
                              body=json.dumps(query))

    connection.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
