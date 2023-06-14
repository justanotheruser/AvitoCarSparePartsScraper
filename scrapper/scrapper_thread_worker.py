import json
import logging
import os
import sys

import dacite
import pika

sys.path.append(os.path.dirname(__file__) + "/..")
from common.queues import SEARCH_QUERIES_QUEUE, FAILED_QUERIES_QUEUE, SCRAPED_ITEMS_QUEUE
from common.types import SearchQuery
from common.config import Config
from driver import create_driver
from web import scrape


def scrapper_thread_worker(cfg: Config, chrome_user_profile_dir: str):
    logging.info('Started')
    driver = create_driver(chrome_user_profile_dir, cfg.scraping.headless)
    logging.info('Chrome driver created')

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.queue_declare(queue=SEARCH_QUERIES_QUEUE)
    channel.queue_declare(queue=FAILED_QUERIES_QUEUE)
    channel.queue_declare(queue=SCRAPED_ITEMS_QUEUE)
    logging.info('Connected to RabbitMQ')

    def read_query(ch, method, properties, body):
        query = json.loads(body)
        logging.info(f'Received query {query}')
        try:
            query = dacite.from_dict(data_class=SearchQuery, data=query)
            scraped_items = scrape(driver, cfg.scraping, query)
            for item in scraped_items:
                channel.basic_publish(exchange='',
                                      routing_key=SCRAPED_ITEMS_QUEUE,
                                      body=item.to_json())
        except Exception:
            logging.exception("Exception in scraping thread")
            channel.basic_publish(exchange='',
                                  routing_key=FAILED_QUERIES_QUEUE,
                                  body=query.to_json())
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=SEARCH_QUERIES_QUEUE, on_message_callback=read_query)
    logging.info('Waiting for messages')
    channel.start_consuming()
    driver.close()
    driver.quit()
    logging.info('Chrome driver quit')
