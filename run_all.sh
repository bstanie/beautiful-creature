#!/bin/bash

start=`date +%s`
root_dir=$PWD

# Scrape everything
python "main.py"

end=`date +%s`
runtime=$((end-start))
echo "Execution time ${runtime} sec" >> "${root_dir}/log.log"

DNSCONFIG=/etc/resolv.conf
if grep -q ec2 "$DNSCONFIG"; then
  sudo shutdown now
fi