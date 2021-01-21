#!/bin/bash

start=`date +%s`

## Scrape search trends
#python social_trends/social_trends.py

## Scrape etoro
cd scrapy_projects/etoro/etoro
#scrapy crawl etoro_dashboard
#scrapy crawl etoro_investor
#
## Scrape marketbeat
cd ../../marketbeat/marketbeat
scrapy crawl marketbeat
#scrapy crawl marketbeat_dashboard

end=`date +%s`
runtime=$((end-start))
echo "Execution time ${runtime} sec"