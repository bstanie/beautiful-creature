import json
import time
from datetime import datetime
import random
from pathlib import Path

import pymongo
import scrapy
from scrapy.utils.project import get_project_settings
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import logging
import os
import sys

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))

logger = logging.root

config = json.load(open(Path(__file__).parent.parent.parent.parent.parent / "config.json", "rb"))
N_TOP_INVESTORS = config["etoro_top_n_investors"]
SAVE_EVERY = config["persist_every"]
settings = get_project_settings()


class EtoroInvestorSpider(scrapy.Spider):
    timestamp = datetime.now().strftime("%d-%m-%y")
    name = "etoro_investor"
    allowed_domains = ["etoro.com"]

    custom_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_DEBUG': True,
        'DOWNLOAD_DELAY': 1,
        'DEPTH_LIMIT': 1,
    }

    connection = pymongo.MongoClient(
        settings['MONGODB_SERVER'],
        settings['MONGODB_PORT']
    )

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.investor_portfolio = []

        import undetected_chromedriver.v2 as uc
        options = uc.ChromeOptions()
        options.add_argument('--no-first-run --no-sandbox --no-service-autorun --password-store=basic')
        self.driver = uc.Chrome(options=options)

        # profile = webdriver.FirefoxProfile()
        # opts = Options()
        # opts.headless = False
        # profile.set_preference("dom.webdriver.enabled", False)
        # profile.set_preference('useAutomationExtension', False)
        # # profile.set_preference('permissions.default.image', 2)
        # # profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        # desired = DesiredCapabilities.FIREFOX
        # profile.update_preferences()
        #
        # self.driver = webdriver.Firefox(
        #     executable_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "geckodriver"),
        #     firefox_options=opts, firefox_profile=profile, desired_capabilities=desired)

    def start_requests(self):
        yield scrapy.Request("https://www.irk.ru", self.parse)

    def _load_scraped_investors(self):

        collection_name = f"{settings['MONGODB_PORTFOLIO_COLLECTION']}_{self.timestamp}"
        db = self.connection[settings['MONGODB_DB']]
        collection = db[collection_name]

        cursor = collection.find({})
        scraped_investors = [usr["investor_name"] for usr in cursor]
        assert len(scraped_investors) == len(set(scraped_investors))
        return scraped_investors

    def _load_investors(self):

        collection_name = f"{settings['MONGODB_INVESTOR_COLLECTION']}_{self.timestamp}"
        db = self.connection[settings['MONGODB_DB']]
        collection = db[collection_name]

        cursor = collection.find({})
        all_investors = [usr["UserName"] for usr in cursor]
        return all_investors

    def parse(self, response, **kwargs):

        all_investor_names = self._load_investors()
        scraped_investor_names = self._load_scraped_investors()
        investor_names = [name for name in all_investor_names if name not in scraped_investor_names]
        print(investor_names)
        investor_urls = [f"https://www.etoro.com/people/{inv_name}/portfolio" for inv_name in investor_names]

        for investor_url in investor_urls:

            portfolio = {}
            investor_name = investor_url.split("/")[-2]
            portfolio["investor_name"] = investor_name
            portfolio["items"] = []
            portfolio["datetime"] = datetime.now().strftime("%y-%m-%d")

            with self.driver:
                self.driver.get(investor_url)
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".ui-table-row.ng-scope.sell")))
            except TimeoutException:
                raise

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

            yield portfolio
