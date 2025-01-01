from time import sleep
import random
import logging
import os
import requests

def random_sleep(min_seconds: int = 5, max_seconds: int = 10):
    sleep(random.uniform(min_seconds, max_seconds))

logger = None

def setup_logging(log_file_path: str):

    global logger
    logger = logging.getLogger("scraping_logger")
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def fetch_url(url, headers, min_sleep, max_sleep, url_type: str):
    try:
        logger.info(f"Fetching {url_type} URL: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logger.info(f"Response status code: {response.status_code} - {response.reason}")
        random_sleep(min_sleep, max_sleep)
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        random_sleep(min_sleep, max_sleep)
        return None  