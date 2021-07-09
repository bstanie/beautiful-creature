import json
import os
import pathlib
from collections import defaultdict

import numpy as np
import pandas as pd
from langdetect import detect
from tqdm import tqdm
from transformers import pipeline

from project_settings import PROJECT_ROOT

sentiment_analyzer = pipeline('sentiment-analysis')


def create_reddit_report():
    dfs = []
    base_path = pathlib.Path(PROJECT_ROOT) / "reddit_scraper" / "data"
    for file_name in tqdm(list(os.walk(base_path))[0][2]):
        file_path = str(base_path / f"{file_name}")
        with open(file_path, "r") as f:
            raw_data = json.load(f)
            data = []

            for item in raw_data:
                if type(item) == list:
                    data.extend(item)
                else:
                    data.append(item)

        result = defaultdict(lambda: defaultdict(int))
        sentiment_result = defaultdict(lambda: defaultdict(list))

        for i in data:
            keyword = i["keyword"]
            comments = i["num_comments"]
            if i["type"] == "posts":
                result[keyword]["num_keyword_posts"] += 1
                result[keyword]["num_comments"] += comments
            elif i["type"] == "comments":
                result[keyword]["num_keyword_comments"] += 1

            text = i["text"]
            if text is not None:
                text = text.replace("\n", " ").strip()
                if not text.startswith("http") \
                        and not text.startswith("[http") \
                        and text != "[removed]" \
                        and 0 < len(text) < 500:
                    try:
                        lang = detect(text)
                        if lang == "en":
                            sentiment = sentiment_analyzer(text)[0]
                            sen_label = sentiment["label"]
                            sen_score = sentiment["score"]
                            if sen_label == "POSITIVE":
                                sentiment_result[keyword]["pos_sentiment"].append(sen_score)
                            elif sen_label == "NEGATIVE":
                                sentiment_result[keyword]["neg_sentiment"].append(sen_score)
                    except Exception as e:
                        print(e)

        for keyword in sentiment_result.keys():
            for sentiment_type in sentiment_result[keyword]:
                scores = sentiment_result[keyword][sentiment_type]
                mean_score = np.mean(scores) / len(scores)
                result[keyword][sentiment_type] = mean_score

        df = pd.DataFrame(result).T
        df["date"] = file_path.split("_")[-1].split(".")[0]
        dfs.append(df)

    stat_df = pd.concat(dfs).reset_index().rename(columns={"index": "keyword"}).sort_values(["keyword", "date"])
    stat_df = stat_df[["date", "keyword", "num_keyword_posts", "num_comments", "num_keyword_comments", "pos_sentiment",
                       "neg_sentiment"]]
    stat_df.to_csv(PROJECT_ROOT / "reddit_scraper" / "reddit_crypto_stat.csv", index=False)
