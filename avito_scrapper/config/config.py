import configparser
import logging
from dataclasses import dataclass
from typing import Optional
import os

import dacite


@dataclass
class InputConfig:
    file: str


@dataclass
class ScrapingConfig:
    start_url: str
    threads: int
    chrome_user_profiles_dir: str


@dataclass
class OutputConfig:
    result_file: str
    images_dir: str


@dataclass
class Miscellaneous:
    scraped_file: str


@dataclass
class Config:
    input: InputConfig
    scraping: ScrapingConfig
    output: OutputConfig
    misc: Miscellaneous


def read_config() -> Optional[Config]:
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), 'avito_scrapper', 'config', 'config.ini')
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
                                                         'chrome_user_profiles_dir']})
    output_cfg = dacite.from_dict(OutputConfig, {'result_file': config['output']['result_file'],
                                                 'images_dir': config['output']['images_dir']})
    misc_cfg = dacite.from_dict(Miscellaneous, {'scraped_file': config['miscellaneous']['scraped_file']})

    return Config(input_cfg, scraping_cfg, output_cfg, misc_cfg)
