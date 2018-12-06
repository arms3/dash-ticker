import requests
import requests_cache
import os
import pandas as pd
import io
import pickle

requests_cache.install_cache()

API_KEY = os.environ.get('QUANDL_API_KEY')
params = {'api_key': API_KEY}
url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.csv'


def fetch(ticker='AAPL,MSFT,GOOG'):
    params['ticker'] = ticker
    r = requests.get(url, params=params)
    if r.status_code != 200:
        params['ticker'] = 'AAPL,MSFT,GOOG'
        r = requests.get(url, params=params)
    df = pd.read_csv(io.StringIO(r.text),parse_dates=['date'])
    return df


def to_html(df):
    return df.head().to_html(classes='table table-striped', border=0,
                index=False)


def get_tickers():
    with open ('ticker.pickle', 'rb') as fp:
        itemlist = pickle.load(fp)
    return itemlist
