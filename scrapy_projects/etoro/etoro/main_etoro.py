import json

from scrapy import cmdline
from scrapy.crawler import CrawlerProcess, CrawlerRunner

import requests
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

from scrapy_projects.etoro.etoro.spiders.etoro_dashboard import EtoroDashboardSpider
from scrapy_projects.etoro.etoro.spiders.etoro_investor import EtoroInvestorSpider

# instrument_mapping = json.loads(requests.get(
#     "http://api.etorostatic.com/sapi/instrumentsmetadata/V1.1/instruments/bulk?bulkNumber=1&totalBulks=1").content)
#
# with open("symbol_mapping.json", "w") as f:
#     json.dump(instrument_mapping, f)

# cmdline.execute("scrapy crawl etoro_dashboard".split())
cmdline.execute("scrapy crawl etoro_investor".split())
