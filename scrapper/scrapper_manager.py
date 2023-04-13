import logging
import os
import shutil
import sys
from threading import Thread

sys.path.append(os.path.dirname(__file__) + "/..")
from common.logger import setup_logger
from common.config import read_config, ScrapingConfig
from scrapper.scrapper_worker import scrapper_worker


def create_new_user_profile_dirs(cfg: ScrapingConfig):
    logging.info(f"Creating Chrome user profile dirs at {cfg.chrome_user_profiles_dir}")
    os.makedirs(cfg.chrome_user_profiles_dir, exist_ok=True)
    shutil.rmtree(cfg.chrome_user_profiles_dir)
    user_profile_dirs = []
    for i in range(cfg.threads):
        user_profile_dir = os.path.join(cfg.chrome_user_profiles_dir, str(i))
        os.makedirs(user_profile_dir)
        user_profile_dirs.append(user_profile_dir)
    logging.info(f'Created Chrome user profile dirs: {user_profile_dirs}')
    return user_profile_dirs


def main():
    setup_logger('scrapper_manager.log')
    cfg = read_config()
    if not cfg:
        return

    try:
        user_profile_dirs = create_new_user_profile_dirs(cfg.scraping)
        scraping_threads = []
        for i in range(cfg.scraping.threads):
            scraping_thread = Thread(target=scrapper_worker, args=(cfg, user_profile_dirs[i]),
                                     name=f'scraping_thread_{i}')
            scraping_thread.start()
            scraping_threads.append(scraping_thread)
    except Exception as e:
        logging.critical(e)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
