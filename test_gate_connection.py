#!/usr/bin/env python3
"""
Test Gate.io API Connection
اختبار الاتصال بـ Gate.io
"""

import os
import sys
import time
import hmac
import hashlib
import json
from urllib.parse import urlencode
import requests
from dotenv import load_dotenv

load_dotenv()


def generate_signature(api_secret, method, url, query_string="", payload_string=""):
    """Generate Gate.io API signature"""
    timestamp = str(int(time.time()))
    
    # Create signature string
    sign_string = f"{method}\n{url}\n{query_string}\n{hashlib.sha512(payload_string.encode()).hexdigest()}\n{timestamp}"
    
    # Generate HMAC signature
    signature = hmac.new(
        api_secret.encode(),
        sign_string.encode(),
        hashlib.sha512
    ).hexdigest()
    
    return {
        "KEY": os.getenv("GATE_API_KEY"),
        "Timestamp": timestamp,
        "SIGN": signature
    }


def test_connection():
    """Test Gate.io API connection"""
    
    print("=" * 60)
    print("🔧 Testing Gate.io API Connection")
    print("=" * 60)
    
    # Check credentials
    api_key = os.getenv("GATE_API_KEY")
    api_secret = os.getenv("GATE_API_SECRET")
    
    if not api_key or not api_secret:
        print("\n❌ Gate.io API credentials not found!")
        print("\nAdd to .env file:")
        print("GATE_API_KEY=your_api_key_here")
        print("GATE_API_SECRET=your_api_secret_here")
        return False
    
    print(f"\n✅ API Key found: {api_key[:10]}...")
    print(f"✅ API Secret found: {'*' * 20}")
    
    # Test 1: Get account balance
    print("\n" + "=" * 60)
    print("Test 1: Get Account Balance")
    print("=" * 60)
    
    try:
        base_url = "https://api.gateio.ws/api/v4"
        endpoint = "/spot/accounts"
        
        headers = generate_signature(api_secret, "GET", endpoint)
        headers["Content-Type"] = "application/json"
        
        response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            balances = response.json()
            print(f"✅ Successfully connected to Gate.io!")
            print(f"\n💰 Account Balance:")
            
            for item in balances:
                currency = item.get("currency")
                available = float(item.get("available", 0))
                locked = float(item.get("locked", 0))
                
                if available > 0 or locked > 0:
                    print(f"   {currency}:")
                    print(f"      Available: {available:.8f}")
                    if locked > 0:
                        print(f"      Locked: {locked:.8f}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Test 2: Get market ticker
    print("\n" + "=" * 60)
    print("Test 2: Get Market Prices")
    print("=" * 60)
    
    try:
        pairs = ["BTC_USDT", "ETH_USDT", "SOL_USDT"]
        
        for pair in pairs:
            endpoint = "/spot/tickers"
            params = {"currency_pair": pair}
            query_string = urlencode(params)
            
            headers = generate_signature(api_secret, "GET", endpoint, query_string)
            headers["Content-Type"] = "application/json"
            
            response = requests.get(
                f"{base_url}{endpoint}?{query_string}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    ticker = data[0]
                    print(f"\n📊 {pair}:")
                    print(f"   Last Price: ${float(ticker.get('last', 0)):.2f}")
                    print(f"   24h High: ${float(ticker.get('high_24h', 0)):.2f}")
                    print(f"   24h Low: ${float(ticker.get('low_24h', 0)):.2f}")
                    print(f"   24h Volume: {float(ticker.get('base_volume', 0)):.2f}")
            else:
                print(f"❌ Failed to get {pair}: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Market data failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print("\n🚀 You're ready to start trading!")
    print("Run: python3 run_gate_trader.py")
    
    return True


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
