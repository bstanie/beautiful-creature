# %%

import json
import os
import pathlib
from collections import defaultdict
from tqdm import tqdm
from transformers import pipeline
import pandas as pd
import numpy as np
import seaborn as sns
import datetime
from matplotlib import pyplot as plt
import plotly.express as px
from binance.client import Client
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from langdetect import detect

# %%
from crypto.preprocessing import create_reddit_report
from project_settings import BINANCE_KEY, BINANCE_SECRET, PROJECT_ROOT

# %%

name_mapping = {"Cardano": "ADAUSDT", "Ripple": "XRPUSDT", "Ethereum": "ETHUSDT", "Dogecoin": "DOGEUSDT",
                "Polkadot": "DOTUSDT", "Litecoin": "LTCUSDT", "Solana": "SOLUSDT",
                "VeChain": "VETUSDT", "FileCoin": "FILUSDT", "Monero": "XMRUSDT"}

symbol = "DOTUSDT"

# %%

client = Client(BINANCE_KEY, BINANCE_SECRET)
klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, start_str="1 Jan, 2021")
print("History size:", len(klines))

# %%

create_reddit_report()

# %%

price = []
time = []
volume = []
for c in klines:
    time.append(datetime.datetime.fromtimestamp(int(str(c[0])[:-3])))
    price.append(float(c[4]))
    volume.append(float(c[5]))

hist_prices = pd.DataFrame({"time": time, "price": price, 'volume': volume})
hist_prices.head()

# %%

plt.figure(figsize=(10, 7))
sns.lineplot(x=hist_prices["time"], y=hist_prices["price"])
plt.title(symbol)

# %%


def fetch_reddit_data(symbol: str):
    history_data_path = PROJECT_ROOT / "reddit_scraper" / 'reddit_crypto_stat.csv'
    df = pd.read_csv(history_data_path)
    df["keyword"] = df["keyword"].map(name_mapping)
    df = df.set_index(['keyword', 'date'])
    df = df.sort_index()
    sub_df = df.loc[symbol, :].copy()
    sub_df.loc[:, sub_df.columns] = StandardScaler().fit_transform(sub_df)
    sub_df.loc[:, sub_df.columns] = SimpleImputer().fit_transform(sub_df)
    sub_df.index = pd.to_datetime(sub_df.index, yearfirst=True)
    return sub_df


def fetch_search_data(symbol: str):
    df = pd.read_json(PROJECT_ROOT / "search_trends.json")
    df.index = pd.to_datetime(df.index, yearfirst=True)
    df[df.columns] = StandardScaler().fit_transform(df)
    df.columns = list(map(lambda x: name_mapping[x], df.columns))
    sub_df = df[[symbol]]
    sub_df.columns = ["search"]
    return sub_df


# %%

hist_reddit = fetch_reddit_data(symbol)
history_prices = hist_prices.set_index("time").loc[hist_reddit.index[0]:]
history_prices[history_prices.columns] = StandardScaler().fit_transform(history_prices)
history_prices.index = history_prices.index.date
history_prices.index.name = "date"
hist_search = fetch_search_data(symbol).loc[hist_reddit.index[0]:]

# %%

px.defaults.width = 1000
px.defaults.height = 600
pd.options.plotting.backend = "plotly"
merge_df = hist_reddit.join(history_prices).join(hist_search)
for col in merge_df.columns:
    merge_df[col] = merge_df[col].rolling(5).mean()
merge_df.plot()

# %%
