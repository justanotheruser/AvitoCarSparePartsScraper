import json
import logging
import os
import sys

import pika

sys.path.append(os.path.dirname(__file__) + "/..")
from common.logger import setup_logger
from common.config import read_config
from common.queues import FAILED_QUERIES_QUEUE


def main():
    setup_logger('failed_queries_handler.log')
    cfg = read_config()
    if not cfg:
        return

    logging.info(f'Failed queries file: {cfg.output.failed_queries_file}')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=FAILED_QUERIES_QUEUE)

    def read_query(ch, method, properties, body):
        query = json.loads(body)
        logging.info(f'Received query {query}')
        with open(cfg.output.failed_queries_file, 'a', encoding='utf-8') as f:
            f.write(str(query) + '\n')
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=FAILED_QUERIES_QUEUE, on_message_callback=read_query)
    logging.info('Waiting for messages')
    channel.start_consuming()
    connection.close()


if __name__ == '__main__':
    main()
