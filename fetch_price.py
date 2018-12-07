import requests
import os
import pandas as pd
import time
import datetime
import redis
import json

r = redis.from_url(os.environ.get("REDIS_URL"))
print(r)

def fetch(ticker='AAPL'):
    API_KEY = os.environ.get('QUANDL_API_KEY')
    params = {'api_key': API_KEY}
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
            # If we get an error code, print it
            if response.status_code != 200:
                print(datetime.datetime.now(), tick, r)
                # Fall back to stale response if we can't fetch new response
                if exists:
                    dfs.append(to_pandas(mjson))
            else:
                mjson = response.json()
                mjson['time'] = time.strftime("%Y/%m/%d")
                r.set(tick, json.dumps(mjson))
                dfs.append(to_pandas(mjson))

    # Return based on the number of tickers fetched
    if len(dfs) == 0:
        return
    elif len(dfs) == 1:
        return dfs[0]
    else:
        return pd.concat(dfs, axis=0)


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
