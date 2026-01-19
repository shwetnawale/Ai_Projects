import ccxt
import pandas as pd

# Connect to Delta India
print("Connecting to Delta India...")
exchange = ccxt.delta({
    'options': {'defaultType': 'future'}, # We want Futures/Derivatives
    'urls': {
        'api': {
            'public': 'https://api.india.delta.exchange',
            'private': 'https://api.india.delta.exchange',
        }
    }
})

try:
    markets = exchange.load_markets()
    print(f"\n✅ Connected! Found {len(markets)} markets.")
    print("Searching for BTC symbols...")
    
    # Filter for BTC
    btc_markets = [m for m in markets if 'BTC' in m]
    
    print("\nAVAILABLE BTC SYMBOLS:")
    print("-" * 30)
    for m in btc_markets:
        print(f"SYMBOL: '{m}'")
        # Print details to help you choose
        details = markets[m]
        print(f"   ID: {details['id']}")
        print(f"   Settlement: {details.get('settle', 'Unknown')}")
        print("-" * 30)
        
except Exception as e:
    print(f"❌ Error: {e}")
    