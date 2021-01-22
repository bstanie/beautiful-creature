# global level settings
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

TOP_N_STOCKS = 1000  # for marketbeat and google trends
SAVE_EACH_N_ITEMS = 25  # for marketbeat and etoro investor scraper
ETORO_TOP_N_INVESTORS = 2000  # for etoro investor
GOOGLE_TRENDS_CHUNK_SIZE = 1  # for google trends