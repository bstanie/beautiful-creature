import time

import pandas as pd
from pytrends.request import TrendReq
from tqdm import tqdm


def clean_stock_name(stock_name):
    return stock_name.replace('Common Stock', "").replace("Ordinary", ""). \
        replace("Inc.", "").replace("Shares", "").replace("Class A", ""). \
        replace("Corporation", "").replace("Corp.", "").replace("Depositary", "").replace("Series A", ""). \
        replace("Series B", "").replace("Holdings", "").replace("Ltd.", "").replace("Class B", ""). \
        replace("Class C", "").strip()


allowed_domains = ['google.com']
start_urls = ['http://google.com/']
nasdaq_stocks = pd.read_csv("nasdaq.csv").sort_values("Market Cap", ascending=False)
nasdaq_stock_symbols = nasdaq_stocks["Symbol"].tolist()
nasdaq_stock_names = nasdaq_stocks["Name"].apply(clean_stock_name).tolist()

chunks = [nasdaq_stock_symbols[i:i + 5] for i in range(0, len(nasdaq_stock_symbols), 5)]

pytrend = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
dataset = []

for chunk in tqdm(chunks[:100]):
    kw_list = [f"{_} stock" for _ in chunk]
    pytrend.build_payload(kw_list, cat=0, timeframe='today 3-m')
    data = pytrend.interest_over_time()
    if not data.empty:
        data = data.drop(labels=['isPartial'], axis='columns')
        dataset.append(data)
    time.sleep(4)

result = pd.concat(dataset, axis=1)
result.to_csv('search_trends.csv')
