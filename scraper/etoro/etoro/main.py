from scrapy import cmdline
import os

if os.path.exists("etoro_dashboard.json"):
    os.remove("etoro_dashboard.json")
else:
    cmdline.execute("scrapy crawl etoro_people -o etoro_dashboard.json ".split())

cmdline.execute("scrapy crawl etoro_investor -o investor_portfolio.json ".split())