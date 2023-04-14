import logging
import os
import sys

sys.path.append(os.path.dirname(__file__) + "/..")
from utils import setup_playground
from common.config import read_config
from scrapper.web import scrape_relevant_items_from_search_results
from common.types import SearchQuery

if __name__ == '__main__':
    cfg = read_config()
    driver = setup_playground()
    try:
        driver.get(
            'https://www.avito.ru/krasnodar/zapchasti_i_aksessuary/zapchasti/dlya_avtomobiley/transmissiya_i_privod-ASgBAgICA0QKJKwJ~GPiDNq1AQ?q=типтроник')
        query = SearchQuery(car_brand='Не важно', car_model='не важно', spare_part='типтроник')
        scraped_items = scrape_relevant_items_from_search_results(driver, query, None)
        print(scraped_items)
    except Exception as e:
        logging.exception(e)
    finally:
        driver.close()
        driver.quit()
