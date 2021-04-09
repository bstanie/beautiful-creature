# global level settings
import logging
import os
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Scrapy settings

TOP_N_STOCKS = 100  # for marketbeat, marketwatch and google trends
ETORO_TOP_N_INVESTORS = 100  # for etoro scrapers

SAVE_EACH_N_ITEMS = 10  # save results periodically to DB

# Google trends settings

GOOGLE_TRENDS_CHUNK_SIZE = 5  # for google trends
GOOGLE_TREND_RETRIES = 10

# External APIs creds

ALPHAVANTAGE_API_KEY = 'F2050WBAIPD4FC1U'
FINNHUB_API_KEY = 'c05vlgn48v6v0bd91prg'


# Logging settings


logger = logging.root
sh = logging.StreamHandler()
fh = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'log.log'))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)
logger.setLevel(logging.INFO)

# Other settings

SLEEP_TIME = 5
