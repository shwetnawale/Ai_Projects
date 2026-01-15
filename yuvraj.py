import ccxt
import pandas as pd
# import pandas_ta as ta
# import delta_rest_client as delta

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
ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
# print(ohlcv)
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)
print(df)

