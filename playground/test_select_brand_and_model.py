import logging
import os
import sys

sys.path.append(os.path.dirname(__file__) + "/..")
from utils import setup_playground
from common.config import read_config
from scrapper.web import select_brand_and_model

if __name__ == '__main__':
    cfg = read_config()
    driver = setup_playground()
    try:
        driver.get(cfg.scraping.start_url)
        select_brand_and_model(driver, 'Hyundai', 'Solaris')
    except Exception as e:
        logging.exception(e)
    finally:
        driver.close()
        driver.quit()
