import json
import os
import re
from datetime import datetime
from time import sleep

import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import logging

import requests

logger = logging.root

ETORO_TOP_N_INVESTORS = 200
SLEEP_TIME = 5


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
              "pagesize": 100,
              "istestaccount": "false",
              "isfund": "false"}

    start_urls = (
        f'https://www.weacom.ru/',
    )
    PAGE_COUNT = 0

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response, **kwargs):

        profile = webdriver.FirefoxProfile()
        opts = Options()
        opts.headless = True
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference('useAutomationExtension', False)
        profile.update_preferences()
        driver = webdriver.Firefox(
            executable_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "geckodriver"),
            firefox_options=opts, firefox_profile=profile)

        objs = self.parse_with_params(driver)
        with open(f"investor_dashboard_{self.timestamp}.json", "w") as f:
            json.dump(objs, f)

    def parse_with_params(self, driver):
        objs = list()
        for page in range(1, 9999):
            try:
                self.PAGE_COUNT += 1
                logger.info(f"Scraping page {self.PAGE_COUNT}")
                self.params["page"] = page
                param_str = "&".join([f"{k}={v}" for k, v in self.params.items()])
                url = 'view-source:http://www.etoro.com/sapi/rankings/rankings?' + param_str
                driver.get(url)
                obj = json.loads(driver.find_element_by_tag_name('pre').text)["Items"]
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
