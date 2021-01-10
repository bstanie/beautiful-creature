from scrapy import cmdline

# cmdline.execute("scrapy crawl etoro_dashboard -o investors_dashboard.json ".split())
cmdline.execute("scrapy crawl marketbeat -o marketbeat.json ".split())
