import os

from scrapy.crawler import CrawlerProcess
from scrapy_projects.marketbeat.marketbeat.spiders.marketbeat import MarketBeatSpider

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MarketBeatSpider)
    process.start()
