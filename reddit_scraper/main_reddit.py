import argparse
import json
import pathlib

from reddit_scraper.applogic.extractor import run_extractor
from s_utils.datetime_utils import get_datetime_borders_from_args

with open(pathlib.Path.cwd().parent / "config.json", "r") as f:
    KEYWORDS = json.load(f)["cryptos"]


def start(args):
    start_timestamp, end_timestamp = get_datetime_borders_from_args(args)
    run_extractor(KEYWORDS, start_timestamp, end_timestamp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start_date", help="Scrape from date %y-%m-%d", required=False)
    parser.add_argument("-e", "--end_date", help="Scrape to date %y-%m-%d", required=False)
    _args = parser.parse_args()
    start(_args)