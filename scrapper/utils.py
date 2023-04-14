import contextlib
import logging

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@contextlib.contextmanager
def second_tab(driver, url):
    original_window_handle = driver.current_window_handle
    driver.switch_to.new_window('tab')
    driver.get(url)
    logging.info(f'Opened {driver.current_url} in another tab')
    yield
    driver.close()
    driver.switch_to.window(original_window_handle)
    WebDriverWait(driver, 1).until(EC.number_of_windows_to_be(1))
