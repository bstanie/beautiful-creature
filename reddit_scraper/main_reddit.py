import argparse
import json
import pathlib

from reddit_scraper.applogic.extractor import run_extractor
from s_utils.datetime_utils import get_datetime_borders_from_args

with open(pathlib.Path.cwd().parent / "config.json", "r") as f:
    config = json.load(f)
    KEYWORDS = config["cryptos"]
    SUBREDDITS = config["subreddits"]


def start(args):
    start_timestamp, end_timestamp = get_datetime_borders_from_args(args, latest_utc_hour=True)
    run_extractor(KEYWORDS, SUBREDDITS, start_timestamp, end_timestamp, args.frequency, args.overwrite)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start_date", help="Scrape from date %y-%m-%d", required=False, default="21-01-01")
    parser.add_argument("-e", "--end_date", help="Scrape to date %y-%m-%d", required=False)
    parser.add_argument("-f", "--frequency", help="Search in time windows with frequency time or day", required=False,
                        default="day")
    parser.add_argument("-o", "--overwrite", help="Overwrite previous data", required=False,
                        default=True)
    _args = parser.parse_args()
    start(_args)
