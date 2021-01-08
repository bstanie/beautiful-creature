import json
import os
import re
import sys
from time import sleep

import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..settings import CHROMEDRIVER_PATH


class PeopleSpider(scrapy.Spider):
    name = "etoro_people"
    allowed_domains = ["etoro.com"]
    start_urls = (
        'https://www.etoro.com/discover/people/results?copyblock=false&period=OneYearAgo&gainmin=10&hasavatar&maxmonthlyriskscoremax=6&dailyddmin=-5&verified&isfund=false&maxmonthlyriskscoremin=1&tradesmin=5&weeklyddmin=-15&profitablemonthspctmin=50&lastactivitymax=30&sort=-copiers&page=1&pagesize=20',
    )

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response, **kwargs):
        # driver = webdriver.Chrome()  # To open a new browser window and navigate it
        # Use headless option to not open a new browser window
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166")

        desired_capabilities = options.to_capabilities()
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                                  desired_capabilities=desired_capabilities)
        objs = list()
        for page in range(1,10):
            sleep(3)
            PAGE_NUM = page
            url = f"https://www.etoro.com/sapi/rankings/rankings/?blocked=false&bonusonly=false&copyblock=false&dailyddmin=-5&gainmin=10&hasavatar=true&isfund=false&istestaccount=false&lastactivitymax=30&maxmonthlyriskscoremax=6&maxmonthlyriskscoremin=1&optin=true&page={PAGE_NUM}&pagesize=100&period=OneYearAgo&profitablemonthspctmin=50&sort=-copiers&tradesmin=5&verified=true&weeklyddmin=-15"
            driver.get(url)
            obj = json.loads(re.sub("<.*?>", "", driver.page_source))["Items"]
            objs.extend(obj)
        print


