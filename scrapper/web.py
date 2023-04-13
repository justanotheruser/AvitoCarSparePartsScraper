import logging
import os
import sys
import time
import typing

from selenium.common import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

sys.path.append(os.path.dirname(__file__) + "/..")
from common.types import SearchQuery, ScrapedItem
from common.config import ScrapingConfig


def try_to_click_ignore_interception(el, timeout):
    start_time = time.time()
    while time.time() < start_time + timeout:
        try:
            el.click()
            break
        except ElementClickInterceptedException:
            time.sleep(1 / 10)
    el.click()


def select_brand_and_model(driver, car_brand, car_model):
    logging.info(f'Selecting brand and model: {car_brand} - {car_model}')

    def select_from_dropdown_list(textbox_xpath, choice, timeout=10):
        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
        WebDriverWait(driver, timeout, ignored_exceptions=ignored_exceptions).until(
            EC.element_to_be_clickable((By.XPATH, textbox_xpath)))
        textbox_el = driver.find_element(By.XPATH, textbox_xpath)
        try_to_click_ignore_interception(textbox_el, timeout=2)

        WebDriverWait(driver, timeout, ignored_exceptions=ignored_exceptions).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//body/div[starts-with(@class, '
                                            '"dropdown-dropdown-box")]/div[starts-with('
                                            '@class, "dropdown-list-")]')))
        choice_xpath = '//div[starts-with(@class, "dropdown-list-")]//span[text()="{0}"]'.format(choice)
        choice_el = driver.find_element(By.XPATH, choice_xpath)
        try_to_click_ignore_interception(choice_el, timeout=2)

    select_from_dropdown_list('//input[@placeholder="Марка авто"]', car_brand)
    select_from_dropdown_list('//input[@placeholder="Модель авто"]', car_model)
    submit_button_el = driver.find_element(By.XPATH, '//button[@data-marker="search-filters/submit-button"]')
    submit_button_el.click()


def scrape(driver, cfg: ScrapingConfig, query: SearchQuery) -> typing.List[ScrapedItem]:
    driver.get(cfg.start_url)
    select_brand_and_model(driver, query.car_brand, query.car_model)
    return []

    '''if not select_spare_part(driver, spare_part):
        return []
    search_result_el = driver.find_element(By.XPATH, '//div[@id="app"]//div[starts-with(@class, "items-items")]')
    search_result = bs(search_result_el.get_attribute('innerHTML'), features="html.parser")
    images_dir = os.path.join(cfg.output.images_dir, car_brand, car_model, spare_part)
    scraped_items = []
    # i = 0
    for item in search_result.contents:
        #    i += 1
        #    if i > 1:
        #        break
        props = scrape_item(driver, item, images_dir)
        sale_ad = ScrapedItem(car_brand=car_brand, car_model=car_model, spare_part=spare_part,
                              url=props['url'], name=props['name'], images=props['images'],
                              description=props['description'],
                              price_value=props['price']['value'],
                              price_currency=props['price']['currency'],
                              seller_name=props['seller']['name'],
                              seller_label=props['seller']['label'])
        scraped_items.append(sale_ad)
    return scraped_items'''
