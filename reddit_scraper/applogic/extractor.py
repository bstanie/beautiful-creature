import logging
import time
import datetime
import tqdm as tqdm

import project_settings
from reddit_scraper.conf import BASE_URLS, SCRAPE_SUBMISSION_COMMENTS
from reddit_scraper.applogic.scraper import scrape_by_number_of_posts, scrape_from_date_to_date, extract_information
from s_utils.db import DataBaseConnector
from reddit_scraper.utils import get_unix_timestamp, get_datetime_from_unix, get_parent_post_ids, \
    make_parent_post_filter_chunks

logger = logging.root
logger.setLevel(logging.INFO)
db_connector = DataBaseConnector()


def run_extractor(keywords, subreddits, start_timestamp, end_timestamp, frequency, overwrite):
    if frequency == "hour":
        look_back = (end_timestamp - start_timestamp).days * 24
        time_delta = datetime.timedelta(hours=1)
    elif frequency == "day":
        look_back = (end_timestamp - start_timestamp).days
        time_delta = datetime.timedelta(days=1)
    else:
        raise ValueError("Frequency should be hour or day")

    if start_timestamp:
        logger.info(
            f"Start scraping all the posts since {start_timestamp} till {end_timestamp} "
            f"in subreddits {subreddits} with keywords: {keywords}")

    log_start_time = time.time()
    current_timestamp = end_timestamp

    for i in tqdm.tqdm(range(look_back)):
        previous_timestamp = current_timestamp - time_delta
        logger.debug(f"\nScraping from {previous_timestamp} to {current_timestamp}")
        _run_extraction_between_timestamps(keywords, subreddits, db_connector, previous_timestamp, current_timestamp, overwrite)
        current_timestamp = previous_timestamp

    log_end_time = time.time()
    logger.info(f"Extraction finished. Time spent:  {log_end_time - log_start_time} seconds")


def _run_extraction_between_timestamps(keywords, subreddits, db_connector, previous_timestamp, current_timestamp, overwrite=False):
    unix_start = int(get_unix_timestamp(previous_timestamp))
    unix_end = int(get_unix_timestamp(current_timestamp))
    time_window = {"$gte": previous_timestamp, "$lt": current_timestamp}

    if len(subreddits) > 1:
        subreddit = ','.join(subreddits)
    else:
        subreddit = subreddits[0]
    for keyword in keywords:

        if overwrite:
            db_connector.delete_items(project_settings.MONGODB_REDDIT_COLLECTION, {"timestamp": time_window,
                                                                                   "keyword": keyword})

        num_docs_for_time_window = db_connector.count_documents(
            project_settings.MONGODB_REDDIT_COLLECTION,
            {"timestamp": time_window,
             "keyword": keyword})

        if num_docs_for_time_window > 0:
            continue

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
            for chu in parent_post_chunks:
                url = BASE_URLS[item_type] + f'&link_id={chu}'
                comments = _extract_by_keyword_and_subreddit(url, item_type, subreddit, keyword, unix_start,
                                                             unix_end,
                                                             log=False)
                if len(comments) > 0:
                    db_connector.save_items(project_settings.MONGODB_REDDIT_COLLECTION, comments)

                total_comments += len(comments)
            logger.debug(
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
        logger.debug(
            f"\nExtracted {len(posts)} '{item_type}' from subreddit '{subreddit}' with a keyword '{keyword}'")

    serialized_posts = extract_information(subreddit, item_type, keyword, posts)

    return serialized_posts
