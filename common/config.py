import configparser
import logging
import os
from dataclasses import dataclass
from typing import Optional

import dacite


@dataclass
class InputConfig:
    file: str


@dataclass
class ScrapingConfig:
    start_url: str
    threads: int
    chrome_user_profiles_dir: str
    images_dir: str
    test_mode: bool
    headless: bool


@dataclass
class OutputConfig:
    result_file: str
    failed_queries_file: str


@dataclass
class Config:
    input: InputConfig
    scraping: ScrapingConfig
    output: OutputConfig


def read_config() -> Optional[Config]:
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'config.ini')
    if not config.read(config_path, encoding='utf-8'):
        logging.critical("[ConfigError] Can't read config.ini")
        return None
    if 'input' not in config:
        logging.critical('[ConfigError] No input settings provided')
        return None
    if 'scraping' not in config:
        logging.critical('[ConfigError] No scraping settings provided')
        return None

    input_cfg = dacite.from_dict(InputConfig, {'file': config['input']['file']})
    scraping_cfg = dacite.from_dict(ScrapingConfig, {'start_url': config['scraping']['start_url'],
                                                     'threads': int(config['scraping']['threads']),
                                                     'chrome_user_profiles_dir': config['scraping'][
                                                         'chrome_user_profiles_dir'],
                                                     'images_dir': config['scraping']['images_dir'],
                                                     'test_mode': config['scraping'].getboolean('test_mode'),
                                                     'headless': config['scraping'].getboolean('headless')})
    output_cfg = dacite.from_dict(OutputConfig, {'result_file': config['output']['result_file'],
                                                 'failed_queries_file': config['output']['failed_queries_file']})

    return Config(input_cfg, scraping_cfg, output_cfg)
