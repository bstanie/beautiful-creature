import json
import os
import re
from datetime import datetime
from time import sleep

import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import logging
logger = logging.root


class EtoroDashboardSpider(scrapy.Spider):
    timestamp = datetime.now().strftime("%d-%m-%y")
    name = "etoro_dashboard"
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
              "pagesize": 1000,
              "istestaccount": "false",
              "isfund": "false"}

    start_urls = (
        f'https://www.etoro.com/',
    )

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response, **kwargs):

        profile = webdriver.FirefoxProfile()
        opts = Options()
        opts.set_headless()
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference('useAutomationExtension', False)
        profile.update_preferences()
        driver = webdriver.Firefox(
            executable_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "geckodriver"),
            firefox_options=opts, firefox_profile=profile)

        objs = self.parse_with_params(driver)
        self.params["dailyddmin"] = -10
        self.params["dailyddmax"] = -6
        objs2 = self.parse_with_params(driver)
        objs.extend(objs2)
        # assert len(set([_["CustomerId"] for _ in objs])) == 3000
        with open(f"investor_dashboard_{self.timestamp}.json", "w") as f:
            json.dump(objs, f)

    def parse_with_params(self, driver):
        objs = list()
        for page in range(1, 99):
            try:
                logger.info(f"Scraping page {page}")
                self.params["page"] = page
                param_str = "&".join([f"{k}={v}" for k, v in self.params.items()])
                url = 'http://www.etoro.com/sapi/rankings/rankings?' + param_str
                driver.get(url)
                obj = json.loads(re.sub("<.*?>", "", driver.page_source))["Items"]
                if len(obj) == 0:
                    break
                objs.extend(obj)
                sleep(5)
            except Exception as e:
                logger.error(e)
        return objs
