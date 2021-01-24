#!/bin/bash

start=`date +%s`
root_dir=$PWD

# Scrape search trends
#python "social_trends/social_trends.py"
#
## Scrape etoro
#cd "${root_dir}/scrapy_projects/etoro/etoro"
#scrapy crawl etoro_dashboard
#scrapy crawl etoro_investor
#
## Scrape marketbeat
#cd "${root_dir}/scrapy_projects/marketbeat/marketbeat"
#scrapy crawl marketbeat_price_target
#scrapy crawl marketbeat_dashboard
#
#end=`date +%s`
#runtime=$((end-start))
#echo "Execution time ${runtime} sec" >> "${root_dir}/logging.log"

DNSCONFIG=/etc/resolv.conf
if grep -q ec2 "$DNSCONFIG"; then
  sudo shutdown now
fi