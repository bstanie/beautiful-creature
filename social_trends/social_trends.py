import time
import random
from datetime import datetime

import pandas as pd
from pytrends.request import TrendReq
from tqdm import tqdm
import re

import os
import sys
import logging

logger = logging.root

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))

from global_settings import TOP_N_STOCKS as TOP_N_COMPANIES, GOOGLE_TRENDS_CHUNK_SIZE as CHUNK_SIZE, PROJECT_ROOT, \
    SAVE_EACH_N_ITEMS

timestamp = datetime.now().strftime("%d-%m-%y")
file_path = os.path.join(PROJECT_ROOT, "social_trends", f'search_trends_{timestamp}.json')


def clean_stock_name(stock_name):
    name = stock_name.replace('Common Stock', "").replace("Ordinary", ""). \
        replace("Inc.", "").replace("Shares", "").replace("Class A", ""). \
        replace("Corporation", "").replace("Corp.", "").replace("Depositary", "").replace("Series A", ""). \
        replace("Series B", "").replace("Holdings", "").replace("Ltd.", "").replace("Class B", ""). \
        replace("Class C", "").replace("Holding", "").replace("Limited", "").replace("Incorporated", ""). \
        replace("Inc", "").replace("Plc", "").replace("plc", "").replace("p.l.c.", "").replace("ADS", ""). \
        replace("ADR", "").replace("& Co.", "").replace("Group", ""). \
        replace("Capital Stock", "").replace("Stock", "").replace("PLC", "").replace(".com", "").replace(
        'American   each representing eight  share', "").replace("Wholesale", "").replace("US", "")
    name = re.sub(r"\(.*?\)", "", name)
    name = re.sub(r"\s{2,}", " ", name).strip()
    return name


def extract_search_data():
    dataset = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            dataset = [pd.read_json(f)]
    logger.info(f"Scraping google trends data for {TOP_N_COMPANIES} top companies")
    nasdaq_stocks = pd.read_csv(os.path.join(PROJECT_ROOT, "nasdaq.csv")).sort_values("Market Cap", ascending=False)
    nyse_stocks = pd.read_csv(os.path.join(PROJECT_ROOT, "nyse.csv")).sort_values("Market Cap", ascending=False)
    stocks = pd.concat([nasdaq_stocks, nyse_stocks]).sort_values("Market Cap", ascending=False).reset_index().iloc[
             :TOP_N_COMPANIES]
    stocks["clean_name"] = stocks["Name"].apply(clean_stock_name)
    stocks = stocks.drop_duplicates(subset="Symbol", inplace=False)
    stock_names = list(zip(stocks["Symbol"], stocks["clean_name"]))
    if len(dataset) == 1:
        stock_names = [s for s in stock_names if s[0] not in dataset[0].columns]
    chunks = [stock_names[i:i + CHUNK_SIZE] for i in range(0, len(stock_names), CHUNK_SIZE)]

    if len(chunks) == 0:
        logger.info("All stocks for current day were already scraped")
        return

    pytrend = TrendReq(hl='en-US', tz=360, timeout=(10, 25))

    for idx, chunk in enumerate(tqdm(chunks)):
        try:
            tickers = [f"{_[0]}" for _ in chunk]
            search_phrases = [f"'{_[0]} stock'" for _ in chunk]
            pytrend.build_payload(search_phrases, cat=0, timeframe='today 3-m')
            data = pytrend.interest_over_time()
            if not data.empty:
                data = data.drop(labels=['isPartial'], axis='columns')
                data.columns = tickers
                dataset.append(data)
            time.sleep(random.randint(4, 10))
        except Exception as e:
            logger.error(e)

        if idx % SAVE_EACH_N_ITEMS == 0:
            result = pd.concat(dataset, axis=1)
            logger.info(f"Google trends - scraped {idx * CHUNK_SIZE} companies")
            with open(file_path, 'w') as f:
                result.to_json(f)

    result = pd.concat(dataset, axis=1)
    logger.info(f"Google trends - scraped {TOP_N_COMPANIES} companies")
    with open(file_path, 'w') as f:
        result.to_json(f)


if __name__ == '__main__':
    extract_search_data()
