import logging
import os
import sys

sys.path.append(os.path.dirname(__file__) + "/..")
from playground_driver import create_playground_driver
from common.config import read_config
from scrapper.web import select_spare_part

ACURA_MDX_PAGE = 'https://www.avito.ru/all/zapchasti_i_aksessuary/zapchasti/dlya_avtomobiley/acura/mdx-ASgBAgICBEQKJKwJ~GPgtg3Slyjitg3Mqig'
ACURA_EL = 'https://www.avito.ru/all/zapchasti_i_aksessuary/zapchasti/dlya_avtomobiley/acura/el-ASgBAgICBEQKJKwJ~GPgtg3Slyjitg2MpCg'


def test_valid_results_are_found():
    driver = create_playground_driver()
    try:
        search_results_found = select_spare_part(driver, 'фильтр')
        assert search_results_found
    except Exception as e:
        logging.exception(e)
    finally:
        driver.close()
        driver.quit()


def test_non_related_results_detected():
    driver = create_playground_driver()
    try:
        driver.get(ACURA_MDX_PAGE)
        search_results_found = select_spare_part(driver, 'робот')
        assert not search_results_found
    except Exception as e:
        logging.exception(e)
    finally:
        driver.close()
        driver.quit()


def test_nothing_is_found():
    driver = create_playground_driver()
    try:
        driver.get(ACURA_EL)
        search_results_found = select_spare_part(driver, 'робот')
        assert not search_results_found
    except Exception as e:
        logging.exception(e)
    finally:
        driver.close()
        driver.quit()


if __name__ == '__main__':
    test_nothing_is_found()
    #test_non_related_results_detected()
    #test_valid_results_are_found()



