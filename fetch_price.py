import requests_cache
import os
import pandas as pd
import io
import time
import datetime


API_KEY = os.environ.get('QUANDL_API_KEY')
REDIS_URL = os.environ.get('REDIS_URL')
params = {'api_key': API_KEY}
url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.csv'

expire_after = datetime.timedelta(days=1)
requests_cache.install_cache(expire_after=expire_after, backend='sqlite')
# requests_cache.backends.RedisCache(connection=my_server)
s = requests_cache.CachedSession()


def make_throttle_hook(timeout=1.0):
    """
    Returns a response hook function which sleeps for `timeout` seconds if
    response is not cached
    """
    def hook(response, *args, **kwargs):
        if not getattr(response, 'from_cache', False):
            print('sleeping')
            time.sleep(timeout)
        return response
    return hook


def fetch(ticker='AAPL,MSFT,GOOG'):
    s.hooks = {'response': make_throttle_hook(1)}
    requests_cache.core.remove_expired_responses()
    dfs = []
    for tick in ticker.split(','):
        params['ticker'] = tick
        r = s.get(url, params=params)
        print(tick, r.from_cache)
        if r.status_code != 200:
            print(r)
        else:
            df = pd.read_csv(io.StringIO(r.text), parse_dates=['date'])
            dfs.append(df)
    if len(dfs) == 0:
        print(ticker, 'Failed to process')
    elif len(dfs) == 1:
        return dfs[0]
    else:
        return pd.concat(dfs, axis=0, ignore_index=True)


def to_html(df):
    return df.head().to_html(classes='table table-striped', border=0,
                             index=False)


def get_tickers():
    ticks = pd.read_csv('tickers_names.csv')
    return ticks
