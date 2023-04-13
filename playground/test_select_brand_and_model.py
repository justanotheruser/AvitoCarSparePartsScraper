import os
import sys

sys.path.append(os.path.dirname(__file__) + "/..")
from playground_driver import create_playground_driver
from common.config import read_config
from scrapper.web import select_brand_and_model


if __name__ == '__main__':
    cfg = read_config()
    driver = create_playground_driver()
    try:
        driver.get(cfg.scraping.start_url)
        select_brand_and_model(driver, 'Hyundai', 'Solaris')
    except Exception:
        pass
    finally:
        driver.close()
        driver.quit()
