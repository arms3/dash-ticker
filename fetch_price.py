import requests
import os
import pandas as pd
import time
import datetime
import redis
import json
import requests_cache


requests_cache.install_cache(expire_after=datetime.timedelta(days=1))
r = redis.from_url(os.environ.get("REDIS_URL"))
print(r)


def fetch(ticker='AAPL'):
    if ticker == '' : return
    API_KEY = os.environ.get('ALPHA_API_KEY')
    params = {'apikey': API_KEY}
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED'

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
                dfs.append(to_pandas(mjson, tick))
                stale = False

        if stale:
            print(tick, 'Fetching from AlphaVantage')
            params['symbol'] = tick
            response = requests.get(url, params=params)
            print(response, response.json().keys())
            # If we get an error code, print it
            if response.status_code != 200 or 'Time Series (Daily)' not in response.json().keys():
                print(datetime.datetime.now(), tick)
                if 'Error Message' in response.json().keys():
                    print(response.json()['Error Message'])
                elif 'Note' in response.json().keys():
                    print(response.json()['Note'])
                # Fall back to stale response if we can't fetch new response
                if exists:
                    dfs.append(to_pandas(mjson, tick))
            else:
                mjson = response.json()
                mjson['time'] = time.strftime("%Y/%m/%d")
                dfs.append(to_pandas(mjson, tick))
                # Would be better to not set key in the first place
                # Set remote cache, update used and delete less update_used
                print('Updating redis cache')
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
    TO_KEEP = 800
    sort = sorted(used.items(), key=lambda kv: kv[1], reverse=True)
    i = len(sort) - 1
    dels = []
    while i >= TO_KEEP and i >= 0:
        dels.append(sort[i][0])
        i -= 1
    if len(dels) > 0:
        print('Pruning', dels)
        r.delete(*dels)


def to_pandas(json, tick):
    # df = pd.DataFrame(json['datatable']['data'], columns=[d['name'] for d in json['datatable']['columns']])
    # df.date = pd.to_datetime(df.date)

    # Alpha vantage version
    df = pd.DataFrame(json['Time Series (Daily)']).T
    df.reset_index(inplace=True)
    df.columns = ['date', 'open', 'high', 'low', 'close', 'adj_close', 'vol',
                  'dividend_amount', 'split coefficient']
    df.date = pd.to_datetime(df.date)
    df['ticker'] = tick
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
