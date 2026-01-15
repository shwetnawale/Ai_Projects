import ccxt 
import pandas as pd
# import pandas_ta as ta
# from delta_rest_client import DeltaRestClient 


exchange = ccxt.delta({
    'apiKey': 'DscZ8vmfSmjMISIvFHj2naxP7YrC2r',
    'secret': 'JbXwOP6TQUm5jPxi8fxzK8SNU1NUyPa7CU8LUYMfqHkAcyN7ErSWHRR5wuBT',
    'options': {'defaultType': 'future'},
    'urls': {
        'api': {
            'public': 'https://api.india.delta.exchange',
            'private': 'https://api.india.delta.exchange',
        }
    }
})

exchange.load_markets()
symbol = 'BTC/USD:USD'
timeframe = '15m'

start_date_str = '2026-01-13 00:00:00'
start_timestamp_ms = int(pd.Timestamp(start_date_str).timestamp() * 1000)

ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=start_timestamp_ms, limit=2000)
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

print(df)

data = open('shwet.csv', 'w')
data.write(df.to_csv(index=False))
data.close()
