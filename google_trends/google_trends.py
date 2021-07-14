import json
import pathlib
import time
import random
from datetime import datetime, timedelta
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


def extract_search_data(keywords):
    dataset = []
    logger.info(f"Scraping google trends data for {len(keywords)} keywords")
    pytrend = AdaptedTrendReq(hl='en-US', tz=360, timeout=(10, 25))

    for idx, keyword in tqdm(enumerate(tqdm(keywords))):
        try:
            end_timestr = datetime.today().strftime("%Y-%m-%d")
            start_timestr = (datetime.today() - timedelta(days=180)).strftime("%Y-%m-%d")
            timeframe = f"{start_timestr} {end_timestr}"
            pytrend.build_payload([keyword], cat=None, timeframe=timeframe)
            data = pytrend.interest_over_time()
            # data = pytrend.get_historical_interest([keyword], year_start=2021, month_start=6,
            #                                        day_start=26, hour_start=0, year_end=2021,
            #                                        month_end=7, day_end=9, sleep=2)
            if not data.empty:
                data = data.drop(labels=['isPartial'], axis='columns')
                data.columns = [keyword]
                dataset.append(data)
            time.sleep(random.randint(2, 10))
        except Exception as e:
            logger.exception(e)
            break

    result = pd.concat(dataset, axis=1)
    logger.info(f"Google trends - scraped {len(keywords)} companies")
    save_to_db(result)


def save_to_db(df):
    connection = pymongo.MongoClient(
        project_settings.MONGODB_SERVER,
        project_settings.MONGODB_PORT)
    google_trends_collection_name = f"{project_settings.MONGODB_GOOGLE_TRENDS_COLLECTION}_by_day"
    db = connection[project_settings.MONGODB_DB_NAME]
    db.drop_collection(google_trends_collection_name)
    google_trends_collection = db[google_trends_collection_name]
    for i, row in df.reset_index().iterrows():
        google_trends_collection.insert_one(dict(row))


if __name__ == '__main__':
    extract_search_data(KEYWORDS)