from social_trends.social_trends import extract_search_data
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os

from scrapy_projects.etoro.etoro.spiders.etoro_dashboard import EtoroDashboardSpider
from scrapy_projects.etoro.etoro.spiders.etoro_investor import EtoroInvestorSpider
from scrapy_projects.marketbeat.marketbeat.spiders.marketbeat_dashboard import MarketBeatDashboardSpider
from scrapy_projects.marketbeat.marketbeat.spiders.marketbeat_price_target import MarketBeatPriceTargetSpider

import scrapy
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

class Scraper:
    def __init__(self):
        settings_file_path = 'scrapy_projects.etoro.etoro.settings'  # The path seen from root, ie. from main.py
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess()
        self.spider1 = EtoroDashboardSpider
        self.spider2 = EtoroInvestorSpider
        self.spider3 = MarketBeatDashboardSpider
        self.spider4 = MarketBeatPriceTargetSpider

    def run_spiders(self):
        self.runner = CrawlerRunner()
        self.crawl()
        reactor.run()

    @defer.inlineCallbacks
    def crawl(self):
        yield self.runner.crawl(self.spider1)
        yield self.runner.crawl(self.spider2)
        yield self.runner.crawl(self.spider3)
        yield self.runner.crawl(self.spider4)
        reactor.stop()

scraper = Scraper()
scraper.run_spiders()
extract_search_data()

