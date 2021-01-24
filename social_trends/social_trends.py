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

from global_settings import TOP_N_STOCKS, GOOGLE_TRENDS_CHUNK_SIZE, PROJECT_ROOT

TOP_N_COMPANIES = TOP_N_STOCKS
CHUNK_SIZE = GOOGLE_TRENDS_CHUNK_SIZE


def clean_stock_name(stock_name):
    name = stock_name.replace('Common Stock', "").replace("Ordinary", ""). \
        replace("Inc.", "").replace("Shares", "").replace("Class A", ""). \
        replace("Corporation", "").replace("Corp.", "").replace("Depositary", "").replace("Series A", ""). \
        replace("Series B", "").replace("Holdings", "").replace("Ltd.", "").replace("Class B", ""). \
        replace("Class C", "").replace("Holding", "").replace("Limited", "").replace("Incorporated", ""). \
        replace("Inc", "").replace("Plc", "").replace("plc", "").replace("p.l.c.", "").replace("ADS", ""). \
        replace("ADR", "").replace("Company", "").replace("& Co.", "").replace("Group", ""). \
        replace("Capital Stock", "").replace("Stock", "").replace("PLC", "").replace(".com", "").replace(
        'American   each representing eight  share', "").replace("Wholesale", "").replace("US", "")
    name = re.sub(r"\(.*?\)", "", name)
    name = re.sub(r"\s{2,}", " ", name).strip()
    return name


def extract_search_data():
    logger.info(f"Scraping google trends data for {TOP_N_COMPANIES} top companies")
    nasdaq_stocks = pd.read_csv(os.path.join(PROJECT_ROOT, "nasdaq.csv")).sort_values("Market Cap", ascending=False)
    nyse_stocks = pd.read_csv(os.path.join(PROJECT_ROOT, "nyse.csv")).sort_values("Market Cap", ascending=False)
    stocks = pd.concat([nasdaq_stocks, nyse_stocks]).sort_values("Market Cap", ascending=False).reset_index().iloc[
             :TOP_N_COMPANIES]
    stocks["clean_name"] = stocks["Name"].apply(clean_stock_name)
    stocks = stocks.drop_duplicates(subset="clean_name", inplace=False)
    stock_names = list(zip(stocks["Symbol"], stocks["clean_name"]))
    stock_names.insert(0, ('GOOG', "Google"))
    chunks = [stock_names[i:i + CHUNK_SIZE] for i in range(0, len(stock_names), CHUNK_SIZE)]

    pytrend = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
    dataset = []

    for idx, chunk in enumerate(tqdm(chunks)):
        try:
            symbols = [f"{_[0]}" for _ in chunk]
            search_phrases = [f"{_[1]} stock" for _ in chunk]
            pytrend.build_payload(search_phrases, cat=0, timeframe='today 3-m')
            data = pytrend.interest_over_time()
            if not data.empty:
                data = data.drop(labels=['isPartial'], axis='columns')
                data.columns = zip(data.columns, symbols)
                dataset.append(data)
            time.sleep(random.randint(3, 8))
        except Exception as e:
            logger.error(e)

    result = pd.concat(dataset, axis=1)
    timestamp = datetime.now().strftime("%d-%m-%y")
    result.to_csv(os.path.join(PROJECT_ROOT, "social_trends", f'search_trends_{timestamp}.csv'))


if __name__ == '__main__':
    extract_search_data()
