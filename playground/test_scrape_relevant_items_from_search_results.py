import logging
import os
import sys

sys.path.append(os.path.dirname(__file__) + "/..")
from utils import setup_playground
from scrapper.web import scrape_relevant_items_from_search_results
from common.types import SearchQuery


def test_irrelevant_search_results(driver):
    driver.get(
        'https://www.avito.ru/krasnodar/zapchasti_i_aksessuary/zapchasti/dlya_avtomobiley/transmissiya_i_privod-ASgBAgICA0QKJKwJ~GPiDNq1AQ?q=типтроник')
    query = SearchQuery(car_brand='Не важно', car_model='не важно', spare_part='типтроник')
    scraped_items = scrape_relevant_items_from_search_results(driver, query, None)
    print(scraped_items)


def test_relevant_results(driver):
    driver.get(
        'https://www.avito.ru/all/zapchasti_i_aksessuary/zapchasti/dlya_avtomobiley/ford/focus-ASgBAgICBEQKJKwJ~GPgtg2cmCjitg3CpSg?q=двигатель')
    query = SearchQuery(car_brand='Не важно', car_model='не важно', spare_part='двигатель')
    scraped_items = scrape_relevant_items_from_search_results(driver, query, r'C:\Users\Sergei\PycharmProjects\AvitoScrapper\playground\images')
    print(scraped_items)


if __name__ == '__main__':
    driver = setup_playground()
    try:
        test_relevant_results(driver)
        # test_irrelevant_search_results(driver)
    except Exception as e:
        logging.exception(e)
    finally:
        driver.close()
        driver.quit()
