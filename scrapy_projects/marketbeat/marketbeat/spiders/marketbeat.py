import json
from io import BytesIO

import scrapy
import pandas as pd


class MarketBeatSpider(scrapy.Spider):
    name = "marketbeat"
    allowed_domains = ["marketbeat.com"]

    nasdaq_stocks = pd.read_csv("nasdaq.csv").sort_values("Market Cap", ascending=False)["Symbol"].tolist()
    nyse_stocks = pd.read_csv("nyse.csv").sort_values("Market Cap", ascending=False)["Symbol"].tolist()

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.price_target = []

    def start_requests(self):
        nasdaq_urls = [
            "https://www.marketbeat.com/scripts/charts/PriceTargetCSV.ashx?prefix={stock_exchange}&Symbol={ticker}".
                format(stock_exchange="NASDAQ", ticker=stock_name) for stock_name in self.nasdaq_stocks
        ]

        nyse_urls = [
            "https://www.marketbeat.com/scripts/charts/PriceTargetCSV.ashx?prefix={stock_exchange}&Symbol={ticker}".
                format(stock_exchange="NYSE", ticker=stock_name) for stock_name in self.nyse_stocks
        ]

        nasdaq_urls.extend(nyse_urls)
        for url in nasdaq_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response, **kwargs):
        price_target = json.loads(pd.read_csv(BytesIO(response.body), sep=",").to_json(orient="records"))
        with open("marketbeat.json", "w") as f:
            stock_info = {"stock": response.url.split("Symbol=")[1], "history": price_target}
            self.price_target.append(stock_info)
            json.dump(self.price_target, f)
