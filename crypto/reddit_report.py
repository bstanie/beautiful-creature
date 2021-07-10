import json
import os
import pathlib
from collections import defaultdict, Counter
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pymongo
from langdetect import detect
from tqdm import tqdm
from transformers import pipeline

import project_settings
from project_settings import PROJECT_ROOT


# sentiment_analyzer = pipeline('sentiment-analysis')

def create_reddit_report():
    dfs = []

    connection = pymongo.MongoClient(
        project_settings.MONGODB_SERVER,
        project_settings.MONGODB_PORT)
    db = connection[project_settings.MONGODB_DB_NAME]
    reddit_collection_name = f"{project_settings.MONGODB_REDDIT_COLLECTION}"
    reddit_collection = db[reddit_collection_name]

    result = defaultdict(lambda: defaultdict(int))
    sentiment_result = defaultdict(lambda: defaultdict(list))
    day_timestamps = []

    step = timedelta(days=1)
    current_dt = reddit_collection.find({}).sort("timestamp", 1)[0]["timestamp"]
    end_dt = reddit_collection.find({}).sort("timestamp", -1)[0]["timestamp"]
    while current_dt < end_dt:
        day_timestamps.append(datetime.combine(current_dt.date(), datetime.min.time()))
        current_dt += step

    for i in tqdm(range(len(day_timestamps) - 1)):
        day_timestamp = day_timestamps[i]
        data = reddit_collection.find({"timestamp": {"$gte": day_timestamps[i], "$lt": day_timestamps[i + 1]}})
        for i in data:
            keyword = i["keyword"]
            comments = i["num_comments"]
            if i["type"] == "posts":
                result[keyword]["num_keyword_posts"] += 1
                result[keyword]["num_comments"] += comments
            elif i["type"] == "comments":
                result[keyword]["num_keyword_comments"] += 1

            # aggregate information from text fields

            if i["text"] is not None and i["title"] is not None:
                text = i["text"] + ". " + i["title"]
            elif i["text"] is not None and i["title"] is None:
                text = i["text"]
            elif i["text"] is None and i["title"] is not None:
                text = i["title"]
            else:
                continue

            text = text.replace("\n", " ").strip()
            if not text.startswith("http") \
                    and not text.startswith("[") \
                    and 0 < len(text) < 500:
                try:
                    lang = detect(text)
                    if lang == "en":
                        # sentiment = sentiment_analyzer(text)[0]
                        # sen_label = sentiment["label"]
                        # sen_score = sentiment["score"]
                        # if sen_label == "POSITIVE":
                        #     sentiment_result[keyword]["pos_sentiment"].append(sen_score)
                        # elif sen_label == "NEGATIVE":
                        #     sentiment_result[keyword]["neg_sentiment"].append(sen_score)
                        text_splitted = text.lower().split()
                        counts = Counter(text_splitted)
                        sentiment_result[keyword]["pos_sentiment"].append(counts["buy"])
                        sentiment_result[keyword]["neg_sentiment"].append(counts["sell"])
                except Exception as e:
                    print(e)

        for keyword in sentiment_result.keys():
            for sentiment_type in sentiment_result[keyword]:
                scores = sentiment_result[keyword][sentiment_type]
                mean_score = np.mean(scores) / len(scores)
                result[keyword][sentiment_type] = mean_score

        df = pd.DataFrame(result).T
        df["timestamp"] = day_timestamp
        dfs.append(df)

    stat_df = pd.concat(dfs).reset_index().rename(columns={"index": "keyword"}).sort_values(["keyword", "date"])
    stat_df = stat_df[["date", "keyword", "num_keyword_posts", "num_comments", "num_keyword_comments", "pos_sentiment",
                       "neg_sentiment"]]
    stat_df.to_csv(pathlib.Path(PROJECT_ROOT) / "data" / "reddit_crypto_stat.csv", index=False)


if __name__ == "__main__":
    create_reddit_report()
