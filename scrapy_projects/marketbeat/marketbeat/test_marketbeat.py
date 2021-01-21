import os

from scrapy.crawler import CrawlerProcess
from scrapy_projects.marketbeat.marketbeat.spiders.marketbeat import MarketBeatSpider
from scrapy_projects.marketbeat.marketbeat.spiders.marketbeat_ranks import MarketBeatDashboardSpider

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MarketBeatDashboardSpider)
    process.start()
