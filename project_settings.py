# global level settings
import logging
import os
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Scrapy settings

TOP_N_STOCKS = 500  # for marketbeat, and google trends

# Google trends settings

GOOGLE_TRENDS_CHUNK_SIZE = 5  # for google trends
GOOGLE_TREND_RETRIES = 10

# External APIs creds

ALPHAVANTAGE_API_KEY = 'F2050WBAIPD4FC1U'
FINNHUB_API_KEY = 'c05vlgn48v6v0bd91prg'
BINANCE_KEY = '9AvSXO3tI4YD96FjOD6WrRLmleOZu3TcINaG6b35RyPMzGj8uELvV7IRImmILI2p'
BINANCE_SECRET = "p0DWdbocE6GDbnXbAJfvshJwh6N3G6tKNnN02y22Ncw55FIh33QrH2bTPQlvLSpt"

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


