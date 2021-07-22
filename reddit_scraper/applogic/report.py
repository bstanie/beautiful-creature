from collections import defaultdict, Counter
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from langdetect import detect
from tqdm import tqdm

import project_settings
from s_utils.db import DataBaseConnector

MESSAGE_MAX_LEN = 1000


def create_reddit_report(frequency, overwrite=False):
    dfs = []

    timestamps_iterator = []

    db_connector = DataBaseConnector()
    if overwrite:
        db_connector.delete_items(project_settings.MONGODB_REDDIT_STAT_COLLECTION, {})

    all_reddit_posts = db_connector.get_items(project_settings.MONGODB_REDDIT_COLLECTION, {})
    current_dt = all_reddit_posts.sort("timestamp", 1)[0]["timestamp"]
    end_dt = all_reddit_posts.sort("timestamp", -1)[0]["timestamp"]

    while current_dt < end_dt:
        if frequency == "day":
            step = timedelta(days=1)
            timestamps_iterator.append(datetime.combine(current_dt.date(), datetime.min.time()))
        elif frequency == "hour":
            step = timedelta(hours=1)
            timestamps_iterator.append(datetime.combine(current_dt.date(), current_dt.time()))
        else:
            raise ValueError
        current_dt += step

    for i in tqdm(range(len(timestamps_iterator) - 1)):

        result = defaultdict(lambda: defaultdict(int))
        sentiment_result = defaultdict(lambda: defaultdict(list))

        current_timestamp = timestamps_iterator[i]
        time_window = {"timestamp": {"$gte": timestamps_iterator[i],
                                     "$lt": timestamps_iterator[i + 1]}}
        existing_report_in_time_window = list(
            db_connector.get_items(project_settings.MONGODB_REDDIT_STAT_COLLECTION, time_window))
        if len(existing_report_in_time_window) > 0:
            continue
        current_date_reddit_posts = db_connector.get_items(project_settings.MONGODB_REDDIT_COLLECTION,
                                                           time_window)
        for reddit_post in current_date_reddit_posts:
            keyword = reddit_post["keyword"]
            comments = reddit_post["num_comments"]
            if reddit_post["type"] == "posts":
                result[keyword]["num_keyword_posts"] += 1
                result[keyword]["num_comments"] += comments
            elif reddit_post["type"] == "comments":
                result[keyword]["num_keyword_comments"] += 1

            # aggregate information from text fields

            if reddit_post["text"] is not None and reddit_post["title"] is not None:
                text = reddit_post["text"] + ". " + reddit_post["title"]
            elif reddit_post["text"] is not None and reddit_post["title"] is None:
                text = reddit_post["text"]
            elif reddit_post["text"] is None and reddit_post["title"] is not None:
                text = reddit_post["title"]
            else:
                continue

            text = text.replace("\n", " ").strip()
            if not text.startswith("http") \
                    and not text.startswith("[") \
                    and 0 < len(text) < MESSAGE_MAX_LEN:
                try:
                    lang = detect(text)
                    if lang == "en":
                        text_splitted = text.lower().split()
                        counts = Counter(text_splitted)
                        sentiment_result[keyword]["mood_buy"].append(counts["buy"])
                        sentiment_result[keyword]["mood_sell"].append(counts["sell"])
                except Exception as e:
                    print(e)

        for keyword in sentiment_result.keys():
            for sentiment_type in sentiment_result[keyword]:
                scores = sentiment_result[keyword][sentiment_type]
                result[keyword][sentiment_type] = sum(scores)

        df = pd.DataFrame(result).T
        df["timestamp"] = current_timestamp
        dfs.append(df)

    stat_df = pd.concat(dfs)
    if not stat_df.empty:
        if "num_keyword_comments" not in stat_df.columns:
            stat_df["num_keyword_comments"] = np.NAN
        stat_df = stat_df.reset_index().rename(columns={"index": "keyword"}).sort_values(["keyword", "timestamp"])
        stat_df = stat_df[
            ["timestamp", "keyword", "num_keyword_posts", "num_comments", "num_keyword_comments", "mood_buy",
             "mood_sell"]]

        db_connector.save_items(project_settings.MONGODB_REDDIT_STAT_COLLECTION, stat_df.to_dict("records"))


if __name__ == "__main__":
    create_reddit_report(frequency="hour")
