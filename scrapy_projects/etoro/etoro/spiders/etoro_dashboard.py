import json
import os
import re
from datetime import datetime
from time import sleep

import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class EtoroDashboardSpider(scrapy.Spider):
    timestamp = datetime.now().strftime("%d-%m-%y")
    name = "etoro_dashboard"
    allowed_domains = ["etoro.com"]
    params = {"hasavatar": "true",
              "copyblock": "false",
              "period": "OneYearAgo",
              "gainmin": 5,
              "maxmonthlyriskscoremax": 6,
              "dailyddmin": -5,
              "verified": "true",
              "maxmonthlyriskscoremin": 1,
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

        objs = list()
        for page in range(1, 99):
            print(f"Scraping page {page}")
            sleep(2)
            self.params["page"] = page
            param_str = "&".join([f"{k}={v}" for k, v in self.params.items()])
            url = 'http://www.etoro.com/sapi/rankings/rankings?' + param_str
            driver.get(url)
            obj = json.loads(re.sub("<.*?>", "", driver.page_source))["Items"]
            if len(obj) == 0:
                break
            objs.extend(obj)

        with open(f"investor_dashboard_{self.timestamp}.json", "w") as f:
            json.dump(objs, f)
