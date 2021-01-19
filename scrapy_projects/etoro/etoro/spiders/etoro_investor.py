import json
import os
import time
from datetime import datetime

import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import os
import sys

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))

from global_settings import SAVE_EACH_N_ITEMS, ETORO_TOP_N_INVESTORS


class EtoroInvestorSpider(scrapy.Spider):
    timestamp = datetime.now().strftime("%d-%m-%y")

    N_TOP_INVESTORS = ETORO_TOP_N_INVESTORS
    SAVE_EACH = SAVE_EACH_N_ITEMS

    name = "etoro_investor"
    allowed_domains = ["etoro.com"]

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.investor_portfolio = []

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

        scraped_investor_names = []
        dashboard_investor_names = []

        if os.path.exists(f"investor_dashboard_{self.timestamp}.json"):
            with open(f"investor_dashboard_{self.timestamp}.json", "r") as f:
                if len(f.read()) != 0:
                    f.seek(0)
                    investors = json.load(f)
                    dashboard_investor_names = [inv["UserName"].lower() for inv in investors]
                    if self.N_TOP_INVESTORS <= len(dashboard_investor_names):
                        dashboard_investor_names = dashboard_investor_names[:self.N_TOP_INVESTORS]
                    else:
                        self.N_TOP_INVESTORS = len(dashboard_investor_names)

        if os.path.exists(f"investor_portfolio_{self.timestamp}.json"):
            with open(f"investor_portfolio_{self.timestamp}.json", "r") as f:
                if len(f.read()) != 0:
                    f.seek(0)
                    investor_portfolio = json.load(f)
                    self.investor_portfolio = investor_portfolio
                    scraped_investor_names = [inv["investor_name"] for inv in investor_portfolio]

        start_urls = [f"https://www.etoro.com/people/{inv_name}/portfolio" for inv_name
                      in dashboard_investor_names if inv_name not in scraped_investor_names]
        for url in start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response, **kwargs):

        print(f"Scraped items: {len(self.investor_portfolio)} of {self.N_TOP_INVESTORS}")

        portfolio = {}
        investor_name = response.url.split("/")[-2]
        portfolio["investor_name"] = investor_name
        portfolio["items"] = []
        portfolio["datetime"] = datetime.now().strftime("%y-%m-%d")

        self.driver.get(response.url)
        time.sleep(5)
        portfolio_elements = self.driver.find_elements_by_css_selector(".ui-table-row.ng-scope.sell")
        for el in portfolio_elements:
            ticker_data = [_.text for _ in el.find_elements_by_css_selector(".ng-binding")][:-6]
            if len(ticker_data) == 6:
                portfolio_item = {"company_ticker": ticker_data[0], "company_name": ticker_data[1],
                                  "type": ticker_data[2], "invested": ticker_data[3],
                                  "profit/loss": ticker_data[4], "value": ticker_data[5]}
            elif len(ticker_data) == 5:
                portfolio_item = {"company_ticker": ticker_data[0], "type": ticker_data[1],
                                  "invested": ticker_data[2],
                                  "profit/loss": ticker_data[3], "value": ticker_data[4]}
            else:
                portfolio_item = {"ERROR": "ERROR"}

            portfolio["items"].append(portfolio_item)

        self.investor_portfolio.append(portfolio)

        if len(self.investor_portfolio) % self.SAVE_EACH == 0:
            print("Saving results to json")
            with open(f"investor_portfolio_{self.timestamp}.json", 'w') as f:
                json.dump(self.investor_portfolio, f)

        if len(self.investor_portfolio) == self.N_TOP_INVESTORS:
            print("Saving final results to json")
            with open(f"investor_portfolio_{self.timestamp}.json", 'w') as f:
                json.dump(self.investor_portfolio, f)
