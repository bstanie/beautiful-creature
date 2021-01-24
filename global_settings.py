# global level settings
import logging
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

TOP_N_STOCKS = 500  # for marketbeat and google trends
SAVE_EACH_N_ITEMS = 25  # for marketbeat, etoro and google trends
ETORO_TOP_N_INVESTORS = 500  # for etoro investor
GOOGLE_TRENDS_CHUNK_SIZE = 2  # for google trends
ALPHAVANTAGE_API_KEY = 'F2050WBAIPD4FC1U'
FINNHUB_API_KEY = 'c05vlgn48v6v0bd91prg'

logger = logging.root
sh = logging.StreamHandler()
fh = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'logging.log'))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)
logger.setLevel(logging.INFO)
