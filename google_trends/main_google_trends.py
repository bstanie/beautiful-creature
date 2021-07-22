import argparse
import json
import pathlib
import time
import random
from datetime import datetime
from typing import List

import pandas as pd
from tqdm import tqdm
import os
import sys
import logging

import project_settings
from project_settings import PROJECT_ROOT
from pytrend import AdaptedTrendReq
from s_utils.datetime_utils import get_datetime_borders_from_args
from s_utils.db import DataBaseConnector

logger = logging.root

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))

with open(pathlib.Path.cwd().parent / "config.json", "r") as f:
    KEYWORDS = json.load(f)["cryptos"]

config = json.load(open(pathlib.Path(PROJECT_ROOT) / "config.json", "rb"))
SAVE_EVERY = config["save_every"]


# def clean_name(keyword):
#     name = keyword.replace('Common Stock', "").replace("Ordinary", ""). \
#         replace("Inc.", "").replace("Shares", "").replace("Class A", ""). \
#         replace("Corporation", "").replace("Corp.", "").replace("Depositary", "").replace("Series A", ""). \
#         replace("Series B", "").replace("Holdings", "").replace("Ltd.", "").replace("Class B", ""). \
#         replace("Class C", "").replace("Holding", "").replace("Limited", "").replace("Incorporated", ""). \
#         replace("Inc", "").replace("Plc", "").replace("plc", "").replace("p.l.c.", "").replace("ADS", ""). \
#         replace("ADR", "").replace("& Co.", "").replace("Group", ""). \
#         replace("Capital Stock", "").replace("Stock", "").replace("PLC", "").replace(".com", "").replace(
#         'American   each representing eight  share', "").replace("Wholesale", "").replace("US", "")
#     name = re.sub(r"\(.*?\)", "", name)
#     name = re.sub(r"\s{2,}", " ", name).strip()
#     return name


class GoogleTrendsExtractor:

    def __init__(self):
        self.db_connector = DataBaseConnector()
        self.pytrend = AdaptedTrendReq(hl='en-US', tz=0, timeout=(10, 25))

    def extract_search_data(self, keywords: List[str], kind: str, start_timestamp, end_timestamp,
                            overwrite=False):

        logger.info(f"Scraping google trends data for {len(keywords)} keywords "
                    f"from {start_timestamp} to {end_timestamp}")

        for keyword in tqdm(keywords):
            self._extract(keyword, start_timestamp, end_timestamp, kind, overwrite)

        logger.info(f"Google trends - scraped {len(keywords)} keywords")

    def _extract(self, keyword, start_timestamp, end_timestamp, kind, overwrite):

        if overwrite:
            delete_result = self.db_connector.delete_items(project_settings.MONGODB_GOOGLE_TRENDS_COLLECTION_HOUR,
                                           {"keyword": keyword})
            logger.info(f"Deleted {delete_result.deleted_count} items for keyword {keyword}")

        existing_data_len = self.db_connector.count_documents(project_settings.MONGODB_GOOGLE_TRENDS_COLLECTION_HOUR,
                                                              {"keyword": keyword})
        existing_data = None
        if existing_data_len > 0:
            existing_data = self.db_connector.get_items(project_settings.MONGODB_GOOGLE_TRENDS_COLLECTION_HOUR,
                                                        {"keyword": keyword})
            latest_timestamp = existing_data.sort("timestamp", -1)[0]["timestamp"]
            start_timestamp = latest_timestamp
            existing_data = pd.DataFrame(existing_data.sort("timestamp", 1)).drop("_id", axis=1)

        start_timestamp_str = start_timestamp.strftime("%Y-%m-%d")
        end_timestamp_str = end_timestamp.strftime("%Y-%m-%d")
        timeframe = f"{start_timestamp_str} {end_timestamp_str}"
        self.pytrend.build_payload([keyword], cat=None, timeframe=timeframe)
        if kind == "hour":
            if (end_timestamp - start_timestamp).seconds / 3600 < 2:
                return pd.DataFrame()
            logger.info(
                f"Scraping google trends data for {keyword} from {start_timestamp} to {end_timestamp}")
            data = self.pytrend.get_historical_interest([keyword], year_start=start_timestamp.year,
                                                        month_start=start_timestamp.month,
                                                        day_start=start_timestamp.day, hour_start=start_timestamp.hour,
                                                        year_end=end_timestamp.year,
                                                        month_end=end_timestamp.month, day_end=end_timestamp.day,
                                                        hour_end=datetime.utcnow().hour,
                                                        sleep=0)
            time.sleep(random.randint(1, 5))
        else:
            raise ValueError("Should be day or hour")
        if not data.empty:
            data = data.drop(labels=['isPartial'], axis='columns')
            data.columns = [keyword]
            if existing_data is not None:
                self._save(data, "by_hour", existing_data=existing_data)
            else:
                self._save(data, "by_hour")
        return data

    def _save(self, new_data: pd.DataFrame, collection_suffix: str, existing_data: pd.DataFrame = None):
        if collection_suffix == "by_hour":
            collection_name = project_settings.MONGODB_GOOGLE_TRENDS_COLLECTION_HOUR
        elif collection_suffix == "by_day":
            collection_name = project_settings.MONGODB_GOOGLE_TRENDS_COLLECTION_DAY
        else:
            raise KeyError
        keyword = new_data.columns[0]
        new_data["keyword"] = keyword
        new_data = new_data.reset_index()
        new_data = new_data.rename(columns={keyword: "value", "date": "timestamp"})
        if existing_data is not None:
            assert existing_data.sort_index()["timestamp"].tolist()[-1] == new_data["timestamp"][0]
            multiplier = new_data[["value"]].iloc[0] / existing_data[["value"]].iloc[-1]
            existing_data[["value"]] *= multiplier
            new_data = existing_data.append(new_data.iloc[1:])
        items = new_data.to_dict("records")
        self.db_connector.delete_items(project_settings.MONGODB_GOOGLE_TRENDS_COLLECTION_HOUR,
                                       {"keyword": keyword})
        self.db_connector.save_items(collection_name, items)


def start(args):
    google_trends_extractor = GoogleTrendsExtractor()
    start_timestamp, end_timestamp = get_datetime_borders_from_args(args, latest_utc_hour=True)
    frequency = args.frequency
    if frequency not in ["hour", "day"]:
        raise RuntimeError("Frequency should be hour or day")
    google_trends_extractor.extract_search_data(KEYWORDS, frequency, start_timestamp,
                                                end_timestamp, args.delete)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start_date", help="Scrape from date %y-%m-%d", required=False, default="21-01-01")
    parser.add_argument("-e", "--end_date", help="Scrape to date %y-%m-%d", required=False)
    parser.add_argument("-f", "--frequency", help="Scrape with frequency (day, hour)", required=False, default="hour")
    parser.add_argument("-d", "--delete", help="Delete previous results for given keywords", required=False,
                        default=False)
    _args = parser.parse_args()
    start(_args)
