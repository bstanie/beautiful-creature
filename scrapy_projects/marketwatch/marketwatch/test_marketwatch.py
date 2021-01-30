import os

from scrapy.crawler import CrawlerProcess

from scrapy_projects.marketwatch.marketwatch.spiders.marketwatch_dashboard import MarketWatchDashboardSpider

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MarketWatchDashboardSpider)
    process.start()
