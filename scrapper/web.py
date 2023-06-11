import logging
import os
import re
import sys
import typing

import requests
import undetected_chromedriver as uc
from selenium.common import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

sys.path.append(os.path.dirname(__file__) + "/..")
from common.types import SearchQuery, ScrapedItem
from common.config import ScrapingConfig
from scrapper.utils import counted_calls, second_tab
from lxml import etree


def scrape(driver: uc.Chrome, cfg: ScrapingConfig, query: SearchQuery) -> typing.List[ScrapedItem]:
    driver.get(cfg.start_url)
    select_brand_and_model(driver, query.car_brand, query.car_model)
    if not select_spare_part(driver, query.spare_part):
        return []

    logging.info(f'Search results page: {driver.current_url} for query {query}')
    images_dir = os.path.join(cfg.images_dir, query.car_brand, query.car_model, query.spare_part)
    return scrape_relevant_items_from_search_results(driver, query, images_dir, cfg.test_mode)


def select_brand_and_model(driver: uc.Chrome, car_brand, car_model):
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


def select_spare_part(driver: uc.Chrome, spare_part) -> bool:
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


def scrape_relevant_items_from_search_results(driver: uc.Chrome, query: SearchQuery, images_dir: typing.Optional[str], test_mode):
    search_result_el = driver.find_element(By.XPATH, '//div[@id="app"]//div[starts-with(@class, "items-items")]')
    search_result_dom = etree.HTML(search_result_el.get_attribute('innerHTML'))
    scraped_items = []
    i = 0
    for item_link in search_result_dom.xpath(
            '//div[starts-with(@class, "iva-item-content")]/div[starts-with(@class, "iva-item-body")]/div[starts-with(@class, "iva-item-titleStep")]//a'):
        if test_mode:
            i += 1
            if i > 2:
                break
        title = item_link.get("title")
        href = 'https://www.avito.ru' + item_link.get("href")
        logging.info(f'Found "{title}": {href}')
        if title.lower().find(query.spare_part) == -1:
            logging.info(f'Item "{title}" is not relevant for query {query}')
            continue
        props = scrape_item(driver, title, href, images_dir)
        scraped_item = ScrapedItem(query=query, url=props['url'], title=props['title'], images=props['images'],
                                   description=props['description'], price_value=props['price']['value'],
                                   price_currency=props['price']['currency'], seller_name=props['seller']['name'],
                                   seller_label=props['seller']['label'])
        logging.debug(scraped_item)
        scraped_items.append(scraped_item)
    return scraped_items


def scrape_item(driver: uc.Chrome, title: str, link_to_item: str, images_dir: typing.Optional[str]):
    with second_tab(driver, link_to_item):
        props = parse_spare_part_page(driver)
        props['url'] = driver.current_url
        props['title'] = title
        if images_dir:
            props['images'] = save_images_from_gallery(driver, images_dir)
        else:
            props['images'] = []
    return props


def parse_spare_part_page(driver):
    TIMEOUT = 10
    content_xpath = '//div[@id="app"]//div[starts-with(@class, "style-item-view-content-")]'
    WebDriverWait(driver, TIMEOUT, ignored_exceptions=(NoSuchElementException,)).until(
        EC.presence_of_element_located((By.XPATH, content_xpath)))

    def get_price():
        price_info = {'value': None, 'currency': None}

        def get_known_price():
            try:
                value_xpath = content_xpath + '//span[starts-with(@class, "style-price-value-main")]/span[' \
                                              '@itemprop="price"]'
                value_el = driver.find_element(By.XPATH, value_xpath)
                value = int(value_el.get_attribute('content'))
                currency_xpath = content_xpath + '//span[starts-with(@class, "style-price-value-main")]/span[' \
                                                 '@itemprop="priceCurrency"]'
                currency_el = driver.find_element(By.XPATH, currency_xpath)
                currency = currency_el.get_attribute('content')
                price_info['value'] = value
                price_info['currency'] = currency
                return True
            except NoSuchElementException:
                return False

        def price_is_unknown():
            price_value_xpath = content_xpath + '//span[starts-with(@class, "style-price-value-string")]/span'
            price_value_el = driver.find_element(By.XPATH, price_value_xpath)
            return price_value_el.get_attribute('innerHTML').find('указана') != -1

        def got_price_info(driver):
            return get_known_price() or price_is_unknown()

        WebDriverWait(driver, TIMEOUT, ignored_exceptions=(NoSuchElementException,)).until(got_price_info)
        return price_info

    def get_description():
        try:
            description_xpath = content_xpath + '//div[@data-marker="item-view/item-description"]'
            WebDriverWait(driver, TIMEOUT, ignored_exceptions=(NoSuchElementException,)).until(
                EC.presence_of_element_located((By.XPATH, description_xpath)))
            description_el = driver.find_element(By.XPATH, description_xpath)
            return description_el.text.strip()
        except NoSuchElementException:
            return None

    def get_seller():
        seller_xpath = content_xpath + '//div[starts-with(@class, "style-seller-info-col")]'

        seller_name_xpath = seller_xpath + '//div[@data-marker="seller-info/name"]'
        WebDriverWait(driver, TIMEOUT, ignored_exceptions=(NoSuchElementException,)).until(
            EC.presence_of_element_located((By.XPATH, seller_name_xpath)))
        name = driver.find_element(By.XPATH, seller_name_xpath).text

        seller_label_xpath = seller_xpath + '//div[@data-marker="seller-info/label"]'
        WebDriverWait(driver, TIMEOUT, ignored_exceptions=(NoSuchElementException,)).until(
            EC.presence_of_element_located((By.XPATH, seller_label_xpath)))
        label = driver.find_element(By.XPATH, seller_label_xpath).text
        return {'name': name, 'label': label}

    return {
        'price': get_price(),
        'description': get_description(),
        'seller': get_seller()
    }


def save_images_from_gallery(driver, images_root_dir):
    gallery_root_xpath = "//div[@id='app']//div[starts-with(@class, 'style-item-view-content')]//div[starts-with(" \
                         "@class, 'gallery-root')]"
    try:
        WebDriverWait(driver, 10, ignored_exceptions=(NoSuchElementException,)).until(
            EC.presence_of_element_located((By.XPATH, gallery_root_xpath)))
        gallery_root_el = driver.find_element(By.XPATH, gallery_root_xpath)
    except (TimeoutException, NoSuchElementException):
        return []

    local_urls = []
    subdir = re.sub('[^a-zA-Z0-9._ -]', '', driver.current_url.split('/')[-1])
    images_dir = os.path.join(images_root_dir, subdir)
    os.makedirs(images_dir, exist_ok=True)

    @counted_calls
    def save_image(image_src):
        response = requests.get(image_src)
        image_filename = str(save_image.calls) + '.jpg'
        image_filename = os.path.join(images_dir, image_filename)
        with open(image_filename, 'wb') as f:
            f.write(response.content)
        local_urls.append(image_filename)

    def save_current_image():
        image_el = gallery_root_el.find_element(
            By.XPATH, "//div[@id='app']//div[starts-with(@class, 'image-frame-wrapper-')]/img")
        save_image(image_el.get_attribute('src'))

    save_current_image()
    for li_el in gallery_root_el.find_elements(By.TAG_NAME, 'li'):
        li_el.click()
        save_current_image()

    return local_urls
