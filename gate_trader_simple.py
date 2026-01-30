#!/usr/bin/env python3
"""
Gate.io Simple Trading Bot - بدون langchain
"""

import time
import hmac
import hashlib
import requests
import json
from datetime import datetime

API_KEY = "465edd938a57d272184fcdd8c4cbdd20"
API_SECRET = "3dda9877d956de7bfa41aa65db4a60205b5abdca33c4aeea1d9a450782d543f3"

BASE_URL = "https://api.gateio.ws/api/v4"

def gen_sign(method, url, query_string='', payload_string=''):
    """Generate Gate.io signature"""
    t = str(int(time.time()))
    m = hashlib.sha512()
    m.update((payload_string or '').encode('utf-8'))
    hashed_payload = m.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string, hashed_payload, t)
    sign = hmac.new(API_SECRET.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': API_KEY, 'Timestamp': t, 'SIGN': sign}

def api_request(method, endpoint, params=None):
    """Make API request"""
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    query_string = ''
    if params:
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    
    sign_headers = gen_sign(method, endpoint, query_string, '')
    headers.update(sign_headers)
    
    url = BASE_URL + endpoint
    if query_string:
        url += '?' + query_string
    
    r = requests.request(method, url, headers=headers)
    return r.json()

def get_balance():
    """Get account balance"""
    data = api_request('GET', '/spot/accounts')
    balance = {}
    if isinstance(data, list):
        for item in data:
            currency = item['currency']
            available = float(item['available'])
            if available > 0:
                balance[currency] = available
    return balance

def get_ticker(pair):
    """Get ticker price"""
    data = api_request('GET', '/spot/tickers', {'currency_pair': pair})
    if data and len(data) > 0:
        return {
            'pair': pair,
            'last': float(data[0]['last']),
            'high': float(data[0]['high_24h']),
            'low': float(data[0]['low_24h']),
            'volume': float(data[0]['base_volume'])
        }
    return None

def main():
    print("=" * 60)
    print("🚀 Gate.io Trading Bot - Simple Version")
    print("=" * 60)
    
    # Get balance
    print("\n💰 Account Balance:")
    balance = get_balance()
    for currency, amount in balance.items():
        print(f"   {currency}: {amount:.8f}")
    
    # Get market prices
    print("\n📊 Market Prices:")
    pairs = ['BTC_USDT', 'ETH_USDT', 'SOL_USDT']
    
    for pair in pairs:
        ticker = get_ticker(pair)
        if ticker:
            print(f"\n{pair}:")
            print(f"   Last: ${ticker['last']:.2f}")
            print(f"   24h High: ${ticker['high']:.2f}")
            print(f"   24h Low: ${ticker['low']:.2f}")
            print(f"   Volume: {ticker['volume']:.2f}")
    
    # Calculate total value in USDT
    total_usdt = balance.get('USDT', 0)
    
    if 'BTC' in balance:
        btc_price = get_ticker('BTC_USDT')
        if btc_price:
            total_usdt += balance['BTC'] * btc_price['last']
    
    if 'ETH' in balance:
        eth_price = get_ticker('ETH_USDT')
        if eth_price:
            total_usdt += balance['ETH'] * eth_price['last']
    
    print("\n" + "=" * 60)
    print(f"💵 Total Portfolio Value: ${total_usdt:.2f} USDT")
    print("=" * 60)
    
    print("\n✅ Connection successful!")
    print("🚀 Ready to trade!")

if __name__ == "__main__":
    main()
