import logging
import os
import sys
import typing

from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

sys.path.append(os.path.dirname(__file__) + "/..")
from common.types import SearchQuery, ScrapedItem
from common.config import ScrapingConfig


def select_brand_and_model(driver, car_brand, car_model):
    logging.info(f'Selecting brand and model: {car_brand} - {car_model}')

    def select_from_dropdown_list(textbox_xpath, choice, timeout=10):
        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
        WebDriverWait(driver, timeout, ignored_exceptions=ignored_exceptions).until(
            EC.element_to_be_clickable((By.XPATH, textbox_xpath)))
        textbox_el = driver.find_element(By.XPATH, textbox_xpath)
        textbox_el.send_keys(choice)
        WebDriverWait(driver, timeout, ignored_exceptions=ignored_exceptions).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//body/div[starts-with(@class, '
                                            '"dropdown-dropdown-box")]/div[starts-with('
                                            '@class, "dropdown-list-")]')))
        choice_xpath = '//div[starts-with(@class, "dropdown-list-")]//span[text()="{0}"]'.format(choice)
        WebDriverWait(driver, timeout, ignored_exceptions=ignored_exceptions).until(
            EC.element_to_be_clickable((By.XPATH, choice_xpath)))
        choice_el = driver.find_element(By.XPATH, choice_xpath)
        choice_el.click()

    select_from_dropdown_list('//input[@placeholder="Марка авто"]', car_brand)
    select_from_dropdown_list('//input[@placeholder="Модель авто"]', car_model)
    submit_button_el = driver.find_element(By.XPATH, '//button[@data-marker="search-filters/submit-button"]')
    submit_button_el.click()


def select_spare_part(driver, spare_part) -> bool:
    '''
    Enters spare part name in search box, presses Enter and waits until the page is loaded
    Opens page with search results
    :param driver:
    :param spare_part: name of spare part to search
    :return: True if search has found something, False if no (relevant) results found
    '''
    logging.info(f'Selecting spare part - {spare_part}')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                    '//div[@id="app"]//div[starts-with(@class, "index-search")]//input[@placeholder="Поиск по объявлениям"]')))
    textbox_el = driver.find_element(By.CLASS_NAME, 'input-input-Zpzc1')
    textbox_el.send_keys(spare_part)
    textbox_el.send_keys(Keys.ENTER)
    WebDriverWait(driver, 10, poll_frequency=0.1).until(EC.title_contains(spare_part))

    def is_search_results_found(dr):
        try:
            search_result_el = dr.find_element(By.XPATH, '//div[@id="app"]//div[starts-with(@class, "items-items")]')
            if len(search_result_el.get_attribute('innerHTML')) > 0:
                return True
        except NoSuchElementException:
            pass
        return False

    def is_no_result(dr):
        try:
            dr.find_element(By.XPATH, '//div[@id="app"]//div[starts-with(@class, "no-results-root")]')
            return True
        except NoSuchElementException:
            pass
        return False

    def is_page_ready(dr):
        return is_search_results_found(dr) or is_no_result(dr)

    def has_you_probably_need_this_categories(dr):
        try:
            dr.find_element(By.XPATH,
                            '//div[@id="app"]//div[starts-with(@class, "index-content")]//div[starts-with(@class, "styles-title")]//div[text()[contains(.,"Скорее всего, вам нужна одна из")]]')
            return True
        except NoSuchElementException:
            pass
        return False

    def nothing_is_found(dr):
        try:
            dr.find_element(By.XPATH,
                            '//div[@id="app"]//div[starts-with(@class, "index-content")]//div[starts-with(@class, "styles-title")]//div[text()[contains(.,"Ничего не нашлось")]]')
            return True
        except NoSuchElementException:
            pass
        return False

    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
    WebDriverWait(driver, 5, ignored_exceptions=ignored_exceptions, poll_frequency=0.1).until(is_page_ready)
    if is_no_result(driver) or has_you_probably_need_this_categories(driver) or nothing_is_found(driver):
        return False
    return True


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
