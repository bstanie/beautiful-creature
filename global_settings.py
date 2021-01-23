# global level settings
import logging
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

TOP_N_STOCKS = 100  # for marketbeat and google trends
SAVE_EACH_N_ITEMS = 25  # for marketbeat and etoro investor scraper
ETORO_TOP_N_INVESTORS = 100  # for etoro investor
GOOGLE_TRENDS_CHUNK_SIZE = 2  # for google trends

logger = logging.root
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler(os.path.join(os.path.dirname(__file__), 'logging.log')))
logger.setLevel(logging.INFO)
