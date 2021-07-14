import os

from scrapy.crawler import CrawlerProcess

from scrapy_projects.etoro.etoro.spiders.etoro_portfolio import EtoroPortfolioSpider
from scrapy_projects.etoro.etoro.spiders.etoro_investor import EtoroInvestorSpider

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(EtoroPortfolioSpider)
    process.start()
