import json
import logging
import os
import sys

import dacite
import pika

sys.path.append(os.path.dirname(__file__) + "/..")
from common.queues import SEARCH_QUERIES_QUEUE
from common.types import SearchQuery
from common.config import Config
from driver import create_driver
from web import scrape


def scrapper_worker(cfg: Config, chrome_user_profile_dir: str):
    logging.info('Started')
    driver = create_driver(chrome_user_profile_dir)
    logging.info('Chrome driver created')

    def read_query(ch, method, properties, body):
        query = json.loads(body)
        logging.info(f'Received query {query}')
        if query == {}:
            logging.info(f'Received command to stop')
            # search_requests_queue.put(None)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            ch.stop_consuming()
            return

        try:
            query = dacite.from_dict(data_class=SearchQuery, data=query)
            scraped_items = scrape(driver, cfg.scraping, query)
            logging.debug(f'Scraped items: {scraped_items}')
            # for item in scraped_items:
            #    scraped_ads_queue.put(item)
            # processed_search_requests_queue.put(search_request)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            logging.exception("Exception in scraping thread")

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=SEARCH_QUERIES_QUEUE)
    channel.basic_consume(queue=SEARCH_QUERIES_QUEUE, on_message_callback=read_query)
    logging.info('Waiting for messages')
    channel.start_consuming()
    driver.close()
    driver.quit()
    logging.info('Chrome driver quit')
