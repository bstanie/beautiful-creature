import random
import requests
from time import sleep, time
from reddit_scraper.utils import get_datetime_from_unix
import logging

logger = logging.root


def make_api_request(base_url, subreddit, keyword, end_timestamp: int = None, start_timestamp: int = None):
    query = base_url.format(keyword=keyword)
    if subreddit != 'all':
        query += f'&subreddit={subreddit}'
    if keyword != 'all':
        query += f'&q={keyword}'
    if start_timestamp:
        query += f'&after={start_timestamp}'
    if end_timestamp:
        query += f'&before={end_timestamp}'
    res = requests.get(query)
    if res.status_code != 200:
        logger.error(res.status_code, res.text)
        return []
    else:
        return res.json()['data']


def get_data_no_starttime(base_url, subreddit, keyword, end_timestamp):
    data = make_api_request(base_url, subreddit, keyword, end_timestamp=end_timestamp)
    if len(data) == 0:
        raise RuntimeError(f"No data was found for the given subreddit: '{subreddit}'")
    return data


def get_time_borders(data):
    first_post_timestamp = data[0]['created_utc']
    last_post_timestamp = data[-1]['created_utc']

    last_post_datetime = get_datetime_from_unix(last_post_timestamp)
    first_post_datetime = get_datetime_from_unix(first_post_timestamp)

    return first_post_datetime, last_post_datetime


def scrape_from_date_to_date(base_url, subreddit, keyword, starttime_unix: int, endtime_unix: int) -> list:
    i = 0
    latest_data = list()
    current_query_last_post_timestamp = endtime_unix
    while current_query_last_post_timestamp > starttime_unix:

        if i == 0:
            data = make_api_request(base_url, subreddit, keyword, end_timestamp=endtime_unix)
        else:
            data = make_api_request(base_url, subreddit, keyword, end_timestamp=current_query_last_post_timestamp)

        if len(data):
            current_query_first_post_timestamp = data[0]['created_utc']
            current_query_first_post_datetime = get_datetime_from_unix(current_query_first_post_timestamp)

            current_query_last_post_timestamp = data[-1]['created_utc']
            current_query_last_post_datetime = get_datetime_from_unix(current_query_last_post_timestamp)

            logger.debug(f'Scraping step {i + 1} (since {current_query_last_post_datetime} till '
                         f'{current_query_first_post_datetime})')

            latest_data.extend(data)
            i += 1
        else:
            break

    sleep(random.randint(1, 4))
    latest_data = list(filter(lambda x: x['created_utc'] > starttime_unix, latest_data))

    logger.debug(f"Items scraped: {len(latest_data)}")
    return latest_data


def scrape_by_number_of_posts(base_url, subreddit, keyword, endtime_unix: int, max_posts: int):
    i = 0
    all_data = list()
    posts_count = 0
    data = []
    while posts_count < max_posts:
        sleep(random.randint(1, 4))
        if i == 0:
            current_end_timestamp = endtime_unix
        else:
            current_end_timestamp = data[-1]['created_utc']
        data = get_data_no_starttime(base_url, subreddit, keyword, end_timestamp=current_end_timestamp)
        posts_count += len(data)
        all_data.extend(data)
        query_first_post_datetime, query_last_post_datetime = get_time_borders(data)
        logger.debug(
            f'Scraping step {i + 1} (since {query_last_post_datetime} till '
            f'{query_first_post_datetime}): {len(data)}')
        i += 1
    return all_data[:max_posts]


def extract_information(subreddit, item_type, keyword, posts):
    data_to_serialize = list()
    for post in posts:
        try:
            obj = {'post_id': post['id'],
                   'link': post.get('full_link'),
                   'timestamp': get_datetime_from_unix(post['created_utc']),
                   'title': post.get('title'),
                   'text': post.get('selftext'),
                   'image': post.get('url'),
                   'subreddit': subreddit,
                   'body': post.get("body"),
                   "keyword": keyword,
                   "type": item_type,
                   "num_comments": post.get("num_comments", 0)
                   }
            data_to_serialize.append(obj)
        except Exception as e:
            logger.debug("Exception:", e)
    return data_to_serialize
