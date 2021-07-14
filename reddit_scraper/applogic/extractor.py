import logging
import time
import datetime
import tqdm as tqdm

import project_settings
from reddit_scraper.conf import SUBREDDITS, BASE_URLS, SCRAPE_SUBMISSION_COMMENTS
from reddit_scraper.applogic.scraper import scrape_by_number_of_posts, scrape_from_date_to_date, extract_information
from s_utils.db import DataBaseConnector
from reddit_scraper.utils import get_unix_timestamp, get_datetime_from_unix, get_parent_post_ids, \
    make_parent_post_filter_chunks

logger = logging.root


def run_extractor(keywords, start_timestamp, end_timestamp):
    db_connector = DataBaseConnector()

    look_back_timedelta = end_timestamp - start_timestamp
    day_delta = datetime.timedelta(1)

    if start_timestamp:
        logger.info(
            f"Start scraping all the posts since {start_timestamp} till {end_timestamp} "
            f"in the following subreddits {SUBREDDITS} with the following keywords: {keywords}")

    log_start_time = time.time()
    this_day_timestamp = end_timestamp

    for i in range(look_back_timedelta.days):
        previous_day_timestamp = this_day_timestamp - day_delta
        logger.info(f"\nScraping from {previous_day_timestamp} to {this_day_timestamp}")

        db_connector.delete_items(project_settings.MONGODB_REDDIT_COLLECTION,
                                  {"timestamp": {"$gte": previous_day_timestamp, "$lt": this_day_timestamp}})

        unix_start = int(get_unix_timestamp(previous_day_timestamp))
        unix_end = int(get_unix_timestamp(this_day_timestamp))
        _run_extraction_between_timestamps(keywords, db_connector, unix_start, unix_end)

        this_day_timestamp = previous_day_timestamp

    log_end_time = time.time()
    logger.info(f"Extraction finished. Time spent:  {log_end_time - log_start_time} seconds")


def _run_extraction_between_timestamps(keywords, db_connector, unix_start, unix_end):
    for subreddit in SUBREDDITS:
        for keyword in keywords:
            logger.debug(f"Scraping keyword '{keyword}'")
            item_type = "posts"
            url = BASE_URLS["posts"]
            posts = _extract_by_keyword_and_subreddit(url, item_type, subreddit, keyword, unix_start, unix_end,
                                                      log=True)

            db_connector.save_items(project_settings.MONGODB_REDDIT_COLLECTION, posts)

            if SCRAPE_SUBMISSION_COMMENTS is True:
                total_comments = 0
                logger.debug("Scraping comments for posts")
                item_type = "comments"
                parent_post_ids = get_parent_post_ids(posts, keyword)
                parent_post_chunks = make_parent_post_filter_chunks(parent_post_ids)
                for chu in tqdm.tqdm(parent_post_chunks):
                    url = BASE_URLS[item_type] + f'&link_id={chu}'
                    comments = _extract_by_keyword_and_subreddit(url, item_type, subreddit, keyword, unix_start,
                                                                 unix_end,
                                                                 log=False)
                    if len(comments) > 0:
                        db_connector.save_items(project_settings.MONGODB_REDDIT_COLLECTION, comments)

                    total_comments += len(comments)
                logger.info(
                    f"Extracted {total_comments} '{item_type}' from subreddit "
                    f"'{subreddit}' with a keyword '{keyword}'")


def _extract_by_keyword_and_subreddit(url, item_type, subreddit, keyword, start_unix_timestamp, end_unix_timestamp,
                                      log=True, max_posts=None):
    logger.debug(f"Scraping type '{item_type}'")
    if max_posts:
        logger.debug(f"Scraping subreddit '{subreddit}' by max posts: {max_posts}")
        posts = scrape_by_number_of_posts(url, subreddit, keyword,
                                          endtime_unix=end_unix_timestamp,
                                          max_posts=max_posts)
    else:
        serialized_start_timestamp = get_datetime_from_unix(start_unix_timestamp)
        logger.debug(f"Scraping posts in subreddit '{subreddit}' from date {serialized_start_timestamp}")
        posts = scrape_from_date_to_date(url, subreddit, keyword,
                                         starttime_unix=start_unix_timestamp,
                                         endtime_unix=end_unix_timestamp)
    if log:
        logger.info(
            f"\nExtracted {len(posts)} '{item_type}' from subreddit '{subreddit}' with a keyword '{keyword}'")

    serialized_posts = extract_information(subreddit, item_type, keyword, posts)

    return serialized_posts
