import json
from collections import defaultdict
from datetime import datetime

from io import BytesIO
import scrapy
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import scrapy
import pandas as pd

import os
import sys

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))

from global_settings import TOP_N_STOCKS, SAVE_EACH_N_ITEMS, PROJECT_ROOT

import logging

logger = logging.root


class MarketWatchDashboardSpider(scrapy.Spider):
    name = "marketwatch_dashboard"
    timestamp = datetime.now().strftime("%d-%m-%y")
    TOP_N_COMPANIES = TOP_N_STOCKS
    SAVE_EACH = SAVE_EACH_N_ITEMS

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.data = []
        profile = webdriver.FirefoxProfile()
        opts = Options()
        opts.set_headless()
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference('useAutomationExtension', False)
        profile.set_preference('permissions.default.image', 2)
        profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

        profile.update_preferences()

        self.driver = webdriver.Firefox(
            executable_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "geckodriver"),
            firefox_options=opts, firefox_profile=profile)


    def start_requests(self):

        nasdaq_stocks = pd.read_csv(os.path.join(PROJECT_ROOT, "nasdaq.csv"))
        nasdaq_stocks["exchange"] = 'NASDAQ'
        nyse_stocks = pd.read_csv(os.path.join(PROJECT_ROOT, "nyse.csv"))
        nyse_stocks["exchange"] = "NYSE"
        stocks = pd.concat([nasdaq_stocks, nyse_stocks])
        stocks = stocks.sort_values("Market Cap", ascending=False, inplace=False)
        stocks = list(zip(stocks["Symbol"], stocks["exchange"]))

        urls = [
            "https://www.marketwatch.com/investing/stock/{symbol}/analystestimates".format(
                symbol=stock[0]) for stock in stocks
        ]

        for url in urls[:self.TOP_N_COMPANIES]:
            yield scrapy.Request(url, self.parse)

    def parse(self, response, **kwargs):

        stock_profile = defaultdict(dict)
        stock_symbol = response.url.split('/')[-2]
        stock_profile['symbol'] = stock_symbol

        tables = response.css(".table.value-pairs.no-heading.font--lato")
        summary = tables[0]
        price_target = tables[1]

        for r in summary.css('tr'):
            key = r.css('td::text')[0].get()
            val = r.css('td::text')[1].get()
            stock_profile['snapshot'][key] = val

        for r in price_target.css('tr'):
            key = r.css('td::text')[0].get()
            val = r.css('td::text')[1].get()
            stock_profile['price_target'][key] = val

        self.data.append(stock_profile)
        if len(self.data) % self.SAVE_EACH == 0:
            logger.info(f"Marketwatch. Scraped: {len(self.data)} companies. Saving...")
            with open(f"marketwatch_dashboard_{self.timestamp}.json", "w") as f:
                json.dump(self.data, f)

        if len(self.data) == self.TOP_N_COMPANIES:
            logger.info(f"Scraped: {len(self.data)} companies. Saving...")
            with open(f"marketwatch_dashboard_{self.timestamp}.json", "w") as f:
                json.dump(self.data, f)
