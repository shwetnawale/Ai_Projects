import ccxt 
import pandas as pd
import pandas_ta as ta
from delta_rest_client import DeltaRestClient


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


