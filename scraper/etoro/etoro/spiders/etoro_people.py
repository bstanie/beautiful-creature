import json
import os
import re
from time import sleep

import scrapy
from selenium import webdriver
from ..settings import CHROMEDRIVER_PATH


class EtoroPeopleSpider(scrapy.Spider):
    name = "etoro_people"
    # allowed_domains = ["etoro.com"]
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

        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166")

        desired_capabilities = options.to_capabilities()
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                                  desired_capabilities=desired_capabilities)
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

        return objs
