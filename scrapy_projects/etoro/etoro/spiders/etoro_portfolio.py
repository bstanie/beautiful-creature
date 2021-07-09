import json
import time
from datetime import datetime
from pathlib import Path
import pymongo
import scrapy
from scrapy.utils.project import get_project_settings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import logging
import os
import sys
import undetected_chromedriver.v2 as uc
from tqdm import tqdm

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))

logger = logging.root

config = json.load(open(Path(__file__).parent.parent.parent.parent.parent / "config.json", "rb"))
N_TOP_INVESTORS = config["etoro_top_n_investors"]
settings = get_project_settings()


class EtoroPortfolioSpider(scrapy.Spider):
    timestamp = datetime.now().strftime("%d-%m-%y")
    name = "etoro_portfolio"
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
        options = uc.ChromeOptions()
        # options.headless = True
        options.add_argument('--no-first-run --no-sandbox --no-service-autorun --password-store=basic')
        self.driver = uc.Chrome(options=options)

    def start_requests(self):
        yield scrapy.Request("https://www.irk.ru", self.parse)

    def _load_scraped_investors(self):

        collection_name = f"{settings['MONGODB_PORTFOLIO_COLLECTION']}_{self.timestamp}"
        db = self.connection[settings['MONGODB_DB']]
        collection = db[collection_name]

        cursor = collection.find({})
        scraped_investors = [usr["investor_name"] for usr in cursor]
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
        investor_urls = [f"https://www.etoro.com/people/{inv_name}/portfolio" for inv_name in investor_names]

        for investor_url in tqdm(investor_urls):

            portfolio = {}
            investor_name = investor_url.split("/")[-2]
            portfolio["investor_name"] = investor_name
            portfolio["items"] = []
            portfolio["datetime"] = datetime.now().strftime("%y-%m-%d")

            with self.driver:
                self.driver.get(investor_url)
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".ui-table-row.ng-scope.sell")))
            except TimeoutException:
                raise RuntimeError("Timeout Error")
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
