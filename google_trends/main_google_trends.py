import argparse
import json
import pathlib
import time
import random
from datetime import datetime, timedelta
from typing import List

import pandas as pd
import pymongo
from tqdm import tqdm
import re
import os
import sys
import logging

import project_settings
from project_settings import PROJECT_ROOT
from pytrend import AdaptedTrendReq
from s_utils.datetime_utils import get_datetime_borders_from_args

logger = logging.root

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))

OUTPUT_FILE_PATH = os.path.join(PROJECT_ROOT, f'search_trends.json')

with open(pathlib.Path.cwd().parent / "config.json", "r") as f:
    KEYWORDS = json.load(f)["cryptos"]

config = json.load(open(pathlib.Path(PROJECT_ROOT) / "config.json", "rb"))
SAVE_EVERY = config["save_every"]
TIMESTAMP = datetime.now().strftime("%d-%m-%y")


def clean_name(keyword):
    name = keyword.replace('Common Stock', "").replace("Ordinary", ""). \
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


def extract_search_data(keywords: List[str], kind: str, start_timestamp_str: str, end_timestamp_str: str):
    dataset = []
    logger.info(f"Scraping google trends data for {len(keywords)} keywords from {start_timestamp_str} to {end_timestamp_str}")
    pytrend = AdaptedTrendReq(hl='en-US', tz=0, timeout=(10, 25))

    for idx, keyword in tqdm(enumerate(tqdm(keywords))):

        timeframe = f"{start_timestamp_str} {end_timestamp_str}"
        pytrend.build_payload([keyword], cat=None, timeframe=timeframe)
        if kind == "day":
            data = pytrend.interest_over_time()
        elif kind == "hour":
            start_timestamp_dt = datetime.strptime(start_timestamp_str, "%Y-%m-%d")
            end_timestamp_dt = datetime.strptime(end_timestamp_str, "%Y-%m-%d")
            data = pytrend.get_historical_interest([keyword], year_start=start_timestamp_dt.year,
                                                   month_start=start_timestamp_dt.month,
                                                   day_start=start_timestamp_dt.day, hour_start=0,
                                                   year_end=end_timestamp_dt.year,
                                                   month_end=end_timestamp_dt.month, day_end=end_timestamp_dt.day,
                                                   sleep=0)
        else:
            raise ValueError("Should be day or hour")
        if not data.empty:
            data = data.drop(labels=['isPartial'], axis='columns')
            data.columns = [keyword]
            dataset.append(data)
        time.sleep(random.randint(2, 10))

    result = pd.concat(dataset, axis=1)
    logger.info(f"Google trends - scraped {len(keywords)} keywords")
    if kind == "day":
        save_to_db(result, "by_day")
    elif kind == "hour":
        save_to_db(result, "by_hour")


def save_to_db(df, collection_suffix):
    connection = pymongo.MongoClient(
        project_settings.MONGODB_SERVER,
        project_settings.MONGODB_PORT)
    google_trends_collection_name = f"{project_settings.MONGODB_GOOGLE_TRENDS_COLLECTION}_{collection_suffix}"
    db = connection[project_settings.MONGODB_DB_NAME]
    db.drop_collection(google_trends_collection_name)
    google_trends_collection = db[google_trends_collection_name]
    for i, row in df.reset_index().iterrows():
        google_trends_collection.insert_one(dict(row))


def start(args):
    start_timestamp, end_timestamp = get_datetime_borders_from_args(args)
    frequency = args.frequency
    if frequency not in ["hour", "day"]:
        raise RuntimeError("Frequency should be hour or day")
    extract_search_data(KEYWORDS, frequency, start_timestamp.strftime("%Y-%m-%d"), end_timestamp.strftime("%Y-%m-%d"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start_date", help="Scrape from date %y-%m-%d", required=False, default="21-01-01")
    parser.add_argument("-e", "--end_date", help="Scrape to date %y-%m-%d", required=False, default="21-06-20")
    parser.add_argument("-f", "--frequency", help="Scrape with frequency (day, hour)", required=False, default="hour")
    _args = parser.parse_args()
    start(_args)
