import json

from io import BytesIO

import scrapy
import pandas as pd

import os
import sys

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))

from global_settings import TOP_N_STOCKS, SAVE_EACH_N_ITEMS, PROJECT_ROOT


class MarketBeatDashboardSpider(scrapy.Spider):
    name = "marketbeat_dashboard"

    TOP_N_COMPANIES = TOP_N_STOCKS
    SAVE_EACH = SAVE_EACH_N_ITEMS

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.data = []

    def start_requests(self):

        nasdaq_stocks = pd.read_csv(os.path.join(PROJECT_ROOT, "nasdaq.csv"))
        nasdaq_stocks["exchange"] = 'NASDAQ'
        nyse_stocks = pd.read_csv(os.path.join(PROJECT_ROOT, "nyse.csv"))
        nyse_stocks["exchange"] = "NYSE"
        stocks = pd.concat([nasdaq_stocks, nyse_stocks])
        stocks = stocks.sort_values("Market Cap", ascending=False, inplace=False)
        stocks = list(zip(stocks["Symbol"], stocks["exchange"]))

        urls = [
            "https://www.marketbeat.com/stocks/{stock_exchange}/{symbol}/".format(stock_exchange=stock[1],
                                                                                 symbol=stock[0]) for stock in stocks
        ]

        for url in urls[:self.TOP_N_COMPANIES]:
            yield scrapy.Request(url, self.parse)

    def parse(self, response, **kwargs):

        stock_profile = {}
        stock_profile["symbol"] = response.url.split("/")[-2]

        overall_rank = response.xpath("//p[@class='bold m-0']/text()").get()
        insider_rank = response.xpath("//div[@class='carousel-item rankInsider']/h3/span/text()").get()
        community_rank = response.xpath("//div[@class='carousel-item rankCommunity']/h3/span/text()").get()
        valuation_rank = response.xpath("//div[@class='carousel-item rankValuation']/h3/span/text()").get()
        dividend_rank = response.xpath("//div[@class='carousel-item rankDividend']/h3/span/text()").get()
        analyst_rank = response.xpath("//div[@class='carousel-item active rankAnalyst']/h3/span/text()").get()

        stock_profile["overall_rank"] = overall_rank
        stock_profile["insider_rank"] = insider_rank
        stock_profile["community_rank"] = community_rank
        stock_profile["valuation_rank"] = valuation_rank
        stock_profile["dividend_rank"] = dividend_rank
        stock_profile["analyst_rank"] = analyst_rank

        self.data.append(stock_profile)

        if len(self.data) % self.SAVE_EACH == 0:
            print(f"Scraped: {len(self.data)} companies. Saving...")
            with open("marketbeat_dashboard.json", "w") as f:
                json.dump(self.data, f)

        if len(self.data) == self.TOP_N_COMPANIES:
            print(f"Scraped: {len(self.data)} companies. Saving...")
            with open("marketbeat_dashboard.json", "w") as f:
                json.dump(self.data, f)
