# global level settings
import logging
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

TOP_N_STOCKS = 1000  # for marketbeat and google trends
SAVE_EACH_N_ITEMS = 25  # for marketbeat and etoro investor scraper
ETORO_TOP_N_INVESTORS = 1000  # for etoro investor
GOOGLE_TRENDS_CHUNK_SIZE = 2  # for google trends

logger = logging.root
sh = logging.StreamHandler()
fh = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'logging.log'))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.setLevel(logging.INFO)
