# global level settings
import logging
import os
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

TOP_N_STOCKS = 2000  # for marketbeat and google trends
SAVE_EACH_N_ITEMS = 50  # for marketbeat, etoro and google trends
ETORO_TOP_N_INVESTORS = 3000  # for etoro investor
GOOGLE_TRENDS_CHUNK_SIZE = 5  # for google trends
GOOGLE_TREND_RETRIES = 10
ALPHAVANTAGE_API_KEY = 'F2050WBAIPD4FC1U'
FINNHUB_API_KEY = 'c05vlgn48v6v0bd91prg'

current_timestamp = datetime.now().strftime("%d-%m-%y")

logger = logging.root
sh = logging.StreamHandler()
fh = logging.FileHandler(os.path.join(os.path.dirname(__file__), f'{current_timestamp}_log.log'))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)
logger.setLevel(logging.INFO)
