import json
import os
import re
import scrapy


class EtoroInvestorSpider(scrapy.Spider):
    N_TOP_INVESTORS = 2000

    name = "etoro_investor"
    allowed_domains = ["etoro.com"]

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.investor_portfolio = []

    def start_requests(self):
        scraped_investor_ids = []
        dashboard_investor_ids = []

        if os.path.exists("investor_dashboard.json"):
            with open("investor_dashboard.json", "r") as f:
                if len(f.read()) != 0:
                    f.seek(0)
                    investors = json.load(f)
                    dashboard_investor_ids = [inv["CustomerId"] for inv in investors][:self.N_TOP_INVESTORS]

        if os.path.exists("investor_portfolio.json"):
            with open("investor_portfolio.json", "r") as f:
                if len(f.read()) != 0:
                    f.seek(0)
                    investor_portfolio = json.load(f)
                    self.investor_portfolio = investor_portfolio
                    scraped_investor_ids = [int(inv["investor_id"]) for inv in investor_portfolio]

        start_urls = ["https://www.etoro.com/sapi/trade-data-real/live/public/portfolios?cid=" + str(inv_id) for inv_id
                      in dashboard_investor_ids if inv_id not in scraped_investor_ids]
        for idx, url in enumerate(start_urls):
            if idx % 10 == 0:
                print(f"Tried {idx} of {len(start_urls)} items")
                print(f"Scraped items: {len(self.investor_portfolio)}")
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
            self.investor_portfolio.append(portfolio)
            json.dump(self.investor_portfolio, f)
