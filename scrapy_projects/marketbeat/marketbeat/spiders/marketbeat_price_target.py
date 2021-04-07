import json

from io import BytesIO

import scrapy
import pandas as pd

import os
import sys

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))

from global_settings import TOP_N_STOCKS, SAVE_EACH_N_ITEMS, PROJECT_ROOT

import logging
logger = logging.root


class MarketBeatPriceTargetSpider(scrapy.Spider):
    name = "marketbeat_price_target"
    allowed_domains = ["marketbeat.com"]


    TOP_N_COMPANIES = TOP_N_STOCKS
    SAVE_EACH = SAVE_EACH_N_ITEMS

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.price_target = []

    def start_requests(self):

        nasdaq_stocks = \
        pd.read_csv(os.path.join(PROJECT_ROOT, "nasdaq.csv")).sort_values("Market Cap", ascending=False)[
            "Symbol"].tolist()
        nyse_stocks = pd.read_csv(os.path.join(PROJECT_ROOT, "nyse.csv")).sort_values("Market Cap", ascending=False)[
            "Symbol"].tolist()

        nasdaq_urls = [
            "https://www.marketbeat.com/scripts/charts/PriceTargetCSV.ashx?prefix={stock_exchange}&Symbol={ticker}".
                format(stock_exchange="NASDAQ", ticker=stock_name) for stock_name in nasdaq_stocks
        ]

        nyse_urls = [
            "https://www.marketbeat.com/scripts/charts/PriceTargetCSV.ashx?prefix={stock_exchange}&Symbol={ticker}".
                format(stock_exchange="NYSE", ticker=stock_name) for stock_name in nyse_stocks
        ]

        nasdaq_urls.extend(nyse_urls)
        for url in nasdaq_urls[:self.TOP_N_COMPANIES]:
            yield scrapy.Request(url, self.parse)

    def parse(self, response, **kwargs):
        price_target = json.loads(pd.read_csv(BytesIO(response.body), sep=",").to_json(orient="records"))
        stock_info = {"stock": response.url.split("Symbol=")[1], "history": price_target}
        self.price_target.append(stock_info)

        if len(self.price_target) % self.SAVE_EACH == 0:
            logger.info(f"Scraped: {len(self.price_target)} stocks. Saving...")
            with open("marketbeat_price_target.json", "w") as f:
                json.dump(self.price_target, f)

        if len(self.price_target) % self.TOP_N_COMPANIES == 0:
            logger.info(f"Scraped: {len(self.price_target)} stocks. Saving...")
            with open("marketbeat_price_target.json", "w") as f:
                json.dump(self.price_target, f)
