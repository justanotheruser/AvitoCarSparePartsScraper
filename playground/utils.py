import os
import shutil
import sys

import undetected_chromedriver as uc

sys.path.append(os.path.dirname(__file__) + "/..")
from common.logger import setup_logger


def create_user_profile_dir():
    user_profile_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'temp')
    os.makedirs(user_profile_dir, exist_ok=True)
    shutil.rmtree(user_profile_dir)
    os.makedirs(user_profile_dir)
    return user_profile_dir


def create_playground_driver():
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument("--user-data-dir={0}".format(create_user_profile_dir()))
    options.page_load_strategy = 'eager'
    return uc.Chrome(options=options, driver_executable_path='../scrapper/undetected_chromedriver.exe',
                     use_subprocess=False)


def setup_playground():
    setup_logger()
    return create_playground_driver()
