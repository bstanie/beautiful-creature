import os

from scrapy.crawler import CrawlerProcess
from scrapy_projects.marketbeat.marketbeat.spiders.marketbeat import MarketBeatSpider
from scrapy_projects.marketbeat.marketbeat.spiders.marketbeat_ranks import MarketBeatRankSpider

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MarketBeatRankSpider)
    process.start()
