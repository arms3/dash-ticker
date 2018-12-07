import requests
import os
import pandas as pd
import time
import datetime
import redis
import json
import requests_cache


requests_cache.install_cache(expire_after=datetime.timedelta(days=5))
r = redis.from_url(os.environ.get("REDIS_URL"))
print(r)


def fetch(ticker='AAPL'):
    API_KEY = os.environ.get('QUANDL_API_KEY')
    params = {'api_key': API_KEY, 'rows': '500'}
    url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json'

    dfs = []
    for tick in ticker.split(','):
        stale = True
        exists = False
        if r.exists(tick):
            print(tick, 'From cache')
            # Get data / timestamp
            mjson = r.get(tick)
            mjson = json.loads(mjson)
            # Update times used
            update_used(tick)
            # Check timestamp
            if check_time(mjson):  # True = Out of date
                exists = True
            else:
                # Otherwise append response
                dfs.append(to_pandas(mjson))
                stale = False

        if stale:
            print(tick, 'Fetching from Qunadl')
            params['ticker'] = ticker
            response = requests.get(url, params=params)
            print(response)
            # If we get an error code, print it
            if response.status_code != 200:
                print(datetime.datetime.now(), tick, r)
                # Fall back to stale response if we can't fetch new response
                if exists:
                    dfs.append(to_pandas(mjson))
            else:
                mjson = response.json()
                mjson['time'] = time.strftime("%Y/%m/%d")
                dfs.append(to_pandas(mjson))
                # Would be better to not set key in the first place
                # Set remote cache, update used and delete less update_used
                r.set(tick, json.dumps(mjson))
                used = update_used(tick)
                clear_less_used(used)

    # Return based on the number of tickers fetched
    if len(dfs) == 0:
        return
    elif len(dfs) == 1:
        return dfs[0]
    else:
        return pd.concat(dfs, axis=0)


# Function to track how many times a key is used
def update_used(ticker):
    used = json.loads(r.get('_used_times'))
    if ticker in used:
        used[ticker] = used[ticker] + 1
    else:
        used[ticker] = 1
    r.set('_used_times', json.dumps(used))
    return used


# Function to delete less popular keys
def clear_less_used(used):
    TO_KEEP = 20
    sort = sorted(used.items(), key=lambda kv: kv[1], reverse=True)
    i = len(sort) - 1
    dels = []
    while i >= TO_KEEP and i >= 0:
        dels.append(sort[i][0])
        i -= 1
    if len(dels) > 0:
        r.delete(*dels)


def to_pandas(json):
    df = pd.DataFrame(json['datatable']['data'], columns=[d['name'] for d in json['datatable']['columns']])
    df.date = pd.to_datetime(df.date)
    return df


def check_time(json):
    dt = datetime.datetime.strptime(json['time'], "%Y/%m/%d")
    return datetime.datetime.now() > dt + datetime.timedelta(days=1)


def to_html(df):
    return df.head().to_html(classes='table table-striped', border=0,
                             index=False)


def get_tickers():
    ticks = pd.read_csv('tickers_names.csv')
    return ticks
