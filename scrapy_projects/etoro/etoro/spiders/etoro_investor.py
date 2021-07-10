import json
import os
from datetime import datetime
from time import sleep

import pymongo
import requests
import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from scrapy.utils.project import get_project_settings
import logging
from pathlib import Path
import undetected_chromedriver.v2 as uc

logger = logging.root
config = json.load(open(Path(__file__).parent.parent.parent.parent.parent / "config.json", "rb"))
ETORO_TOP_N_INVESTORS = config["etoro_top_n_investors"]
SLEEP_TIME = config["sleep_time"]
settings = get_project_settings()
TIMESTAMP = datetime.now().strftime("%d-%m-%y")

class EtoroInvestorSpider(scrapy.Spider):

    name = "etoro_investor"
    allowed_domains = ["etoro.com"]
    params = {"hasavatar": "true",
              "copyblock": "false",
              "period": "OneYearAgo",
              "gainmin": 5,
              "dailyddmin": -5,
              "dailyddmax": 0,
              "verified": "true",
              "maxmonthlyriskscoremin": 1,
              "maxmonthlyriskscoremax": 6,
              "tradesmin": 5,
              "weeklyddmin": -15,
              "profitablemonthspctmin": 50,
              "lastactivitymax": 30,
              "sort": "-copiers",
              "page": 0,
              "pagesize": 100,
              "istestaccount": "false",
              "isfund": "false"}

    start_urls = (
        f'https://www.irk.ru/',
    )
    PAGE_COUNT = 0

    def drop_existing_collection(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        investor_collection_name = f"{settings['MONGODB_INVESTOR_COLLECTION']}"
        db = connection[settings['MONGODB_DB']]
        collection = db[investor_collection_name]
        collection.delete_many({"timestamp": TIMESTAMP})

    def start_requests(self):
        self.drop_existing_collection()
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response, **kwargs):

        # profile = webdriver.FirefoxProfile()
        # opts = Options()
        # opts.headless = True
        # profile.set_preference("dom.webdriver.enabled", False)
        # profile.set_preference('useAutomationExtension', False)
        # profile.update_preferences()
        # driver = webdriver.Firefox(
        #     executable_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "geckodriver"),
        #     firefox_options=opts, firefox_profile=profile)

        options = uc.ChromeOptions()
        options.headless = True
        options.add_argument('--no-first-run --no-sandbox --no-service-autorun --password-store=basic')
        self.driver = uc.Chrome(options=options)

        objs = self.parse_with_params()
        for obj in objs:
            yield obj

    def parse_with_params(self):
        objs = list()
        for page in range(1, 9999):
            try:
                self.PAGE_COUNT += 1
                logger.info(f"Scraping page {self.PAGE_COUNT}")
                self.params["page"] = page
                param_str = "&".join([f"{k}={v}" for k, v in self.params.items()])
                url = 'http://www.etoro.com/sapi/rankings/rankings?' + param_str
                self.driver.get(url)
                obj = json.loads(self.driver.find_element_by_tag_name('pre').text)["Items"]
                if len(obj) == 0:
                    break
                objs.extend(obj)
                if len(objs) > ETORO_TOP_N_INVESTORS:
                    objs = objs[:ETORO_TOP_N_INVESTORS]
                    break
                sleep(SLEEP_TIME)
            except Exception as e:
                logger.error(e)
        return objs
