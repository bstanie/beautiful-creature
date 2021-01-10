import json
import os
import re
import scrapy


N_TOP_INVESTORS = 500


class EtoroInvestorSpider(scrapy.Spider):
    name = "etoro_investor"
    allowed_domains = ["etoro.com"]
    params = {}
    investor_portfolios = []
    scraped_investor_ids = []
    dashboard_investor_ids = []
    if os.path.exists("investors_dashboard.json"):
        with open("investors_dashboard.json") as f:
            investors = json.load(f)
            dashboard_investor_ids = [inv["CustomerId"] for inv in investors][:N_TOP_INVESTORS]

    if os.path.exists("investor_portfolio.json"):
        with open("investor_portfolio.json") as f:
            if len(f.read()) != 0:
                f.seek(0)
                investor_portfolios = json.load(f)
                scraped_investor_ids = [int(inv["investor_id"]) for inv in investor_portfolios]

    # instrument_mapping = json.loads(requests.get(
    #     "http://api.etorostatic.com/sapi/instrumentsmetadata/V1.1/instruments/bulk?bulkNumber=1&totalBulks=1").content)

    def start_requests(self):
        start_urls = ["https://www.etoro.com/sapi/trade-data-real/live/public/portfolios?cid=" + str(inv_id) for inv_id
                      in self.dashboard_investor_ids if inv_id not in self.scraped_investor_ids]
        for url in start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response, **kwargs):
        substr = re.findall("var model = (.*)\}\]\}", str(response.body))
        portfolio = {}
        if len(substr) == 1:
            portfolio = substr[0] + "}]}"
            portfolio = json.loads(portfolio)
        elif len(substr) == 0:
            substr = re.findall("var model = (.*)\]\}", str(response.body))
            portfolio = substr[0] + "]}"
            portfolio = json.loads(portfolio)
        investor_id = response.url.split("cid=")[1]
        portfolio["investor_id"] = investor_id

        with open("investor_portfolio.json", 'w') as f:
            self.investor_portfolios.append(portfolio)
            json.dump(self.investor_portfolios, f)
