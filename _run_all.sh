#!/bin/bash

echo 'start job'
start=`date +%s`
root_dir=$PWD

# Scrape search trends
echo 'start google'
python "social_trends/social_trends.py"

# Scrape etoro
echo 'start etoro'
cd "${root_dir}/scrapy_projects/etoro/etoro"
scrapy crawl etoro_dashboard
scrapy crawl etoro_investor

# Scrape marketbeat
echo 'start marketbeat'
cd "${root_dir}/scrapy_projects/marketbeat/marketbeat"
scrapy crawl marketbeat_price_target
scrapy crawl marketbeat_dashboard

end=`date +%s`
runtime=$((end-start))
echo "Execution time ${runtime} sec"
