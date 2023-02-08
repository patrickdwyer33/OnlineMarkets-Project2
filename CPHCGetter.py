import pandas as pd
import requests
import json
import sys

def fetch_daily_data(symbol, start, end, granularity):
    pair_split = symbol.split('/')
    symbol = pair_split[0] + '-' + pair_split[1]
    url = 'https://api.pro.coinbase.com/products/'+symbol+'/candles?start='+start+'&end='+end+'&granularity='+granularity
    response = requests.get(url)
    if response.status_code == 200:  # check to make sure the response from server is good
        data = pd.DataFrame(json.loads(response.text), columns=['unix', 'low', 'high', 'open', 'close', 'volume'])
        data['date'] = pd.to_datetime(data['unix'], unit='s')  # convert to a readable date
        if data is None:
            print("Did not return any data from Coinbase for this symbol")
        else:
            data.to_csv('coinbase.csv', index=False)
            #data.to_csv('Coinbase_'+symbol+'_dailydata_'+start+'_'+end+'_'+granularity+'.csv', index=False)
    else:
        print("Did not receieve OK response from Coinbase API")

pair = 'ETH/USD'
start = '2021-10-10T12:00:00'
end = '2022-04-22T12:00:00'
granularity = '86400'
fetch_daily_data(pair, start, end, granularity)
