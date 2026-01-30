#!/usr/bin/env python3
"""
AXUUSD Trading Strategy - High Risk High Reward
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
    t = str(int(time.time()))
    m = hashlib.sha512()
    m.update((payload_string or '').encode('utf-8'))
    hashed_payload = m.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string, hashed_payload, t)
    sign = hmac.new(API_SECRET.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': API_KEY, 'Timestamp': t, 'SIGN': sign}

def api_request(method, endpoint, params=None, data=None):
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    query_string = ''
    payload_string = ''
    
    if params:
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    
    if data:
        payload_string = json.dumps(data)
    
    sign_headers = gen_sign(method, endpoint, query_string, payload_string)
    headers.update(sign_headers)
    
    url = BASE_URL + endpoint
    if query_string:
        url += '?' + query_string
    
    if method == 'GET':
        r = requests.get(url, headers=headers)
    elif method == 'POST':
        r = requests.post(url, headers=headers, data=payload_string)
    else:
        return None
    
    return r.json()

def get_balance():
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
    data = api_request('GET', '/spot/tickers', {'currency_pair': pair})
    if data and len(data) > 0:
        return {
            'pair': pair,
            'last': float(data[0]['last']),
            'high': float(data[0]['high_24h']),
            'low': float(data[0]['low_24h']),
            'volume': float(data[0]['base_volume']),
            'change': float(data[0].get('change_percentage', 0))
        }
    return None

def get_currency_pairs():
    """Get all available trading pairs"""
    data = api_request('GET', '/spot/currency_pairs')
    pairs = []
    if isinstance(data, list):
        for item in data:
            if item.get('trade_status') == 'tradable':
                pairs.append(item['id'])
    return pairs

def place_order(pair, side, amount, price=None):
    """Place order - market or limit"""
    order_data = {
        'currency_pair': pair,
        'side': side,
        'amount': str(amount),
        'type': 'market' if price is None else 'limit'
    }
    
    if price:
        order_data['price'] = str(price)
    
    result = api_request('POST', '/spot/orders', data=order_data)
    return result

def main():
    print("=" * 60)
    print("🚀 AXUUSD Trading Strategy")
    print("=" * 60)
    
    # Check if AXUUSD exists
    print("\n🔍 جاري البحث عن AXUUSD...")
    
    pairs = get_currency_pairs()
    axuusd_pairs = [p for p in pairs if 'AXU' in p.upper()]
    
    print(f"\n📊 الأزواج المتاحة مع AXU:")
    if axuusd_pairs:
        for pair in axuusd_pairs:
            ticker = get_ticker(pair)
            if ticker:
                print(f"\n{pair}:")
                print(f"   السعر: ${ticker['last']:.8f}")
                print(f"   التغير 24h: {ticker['change']:.2f}%")
                print(f"   الحجم: {ticker['volume']:.2f}")
    else:
        print("❌ AXUUSD مش موجود على Gate.io")
        print("\n💡 العملات المتاحة للتداول عالي المخاطر:")
        
        # Find high volatility coins
        volatile_pairs = []
        test_pairs = ['BTC_USDT', 'ETH_USDT', 'SOL_USDT', 'PEPE_USDT', 'SHIB_USDT', 
                      'DOGE_USDT', 'WIF_USDT', 'BONK_USDT']
        
        for pair in test_pairs:
            ticker = get_ticker(pair)
            if ticker:
                volatile_pairs.append(ticker)
        
        # Sort by change percentage
        volatile_pairs.sort(key=lambda x: abs(x['change']), reverse=True)
        
        print("\n🔥 أعلى العملات تقلباً (فرصة ربح أكبر):")
        for i, ticker in enumerate(volatile_pairs[:5], 1):
            print(f"\n{i}. {ticker['pair']}:")
            print(f"   السعر: ${ticker['last']:.8f}")
            print(f"   التغير 24h: {ticker['change']:.2f}%")
            print(f"   الحجم: {ticker['volume']:.2f}")
    
    # Get balance
    print("\n" + "=" * 60)
    print("💰 رصيدك الحالي:")
    balance = get_balance()
    usdt_balance = balance.get('USDT', 0)
    
    for currency, amount in balance.items():
        print(f"   {currency}: {amount:.8f}")
    
    print(f"\n💵 USDT المتاح للتداول: ${usdt_balance:.2f}")
    
    # Trading strategy
    print("\n" + "=" * 60)
    print("📈 استراتيجية التداول عالي المخاطر:")
    print("=" * 60)
    
    print("""
⚠️  تحذير مهم:
- التداول عالي المخاطر = احتمال خسارة كل الفلوس
- مفيش ضمان للربح
- السوق متقلب جداً

💡 استراتيجيات للربح السريع:

1️⃣ Scalping (سكالبينج):
   - شراء وبيع سريع جداً
   - استهداف ربح 1-3% في دقائق
   - محتاج متابعة مستمرة

2️⃣ Momentum Trading:
   - شراء العملات اللي طالعة بقوة
   - البيع عند أول إشارة هبوط
   - ربح محتمل: 5-20%

3️⃣ High Volatility Coins:
   - تداول العملات الصغيرة المتقلبة
   - ربح محتمل: 50-500%
   - خطر خسارة: 50-100%

4️⃣ Leverage Trading (Futures):
   - استخدام الرافعة المالية
   - ربح محتمل: 100-1000%
   - خطر تصفية الحساب كامل

🎯 التوصية:
- ابدأي بـ 20% من رصيدك بس
- حطي Stop Loss دايماً
- ما تطمعيش - خدي الربح وامشي
- اتعلمي من كل صفقة
""")
    
    print("\n" + "=" * 60)
    print("🤖 عايزة أنفذ استراتيجية معينة؟")
    print("=" * 60)
    print("""
اختاري:
1. Scalping على BTC/ETH (ربح صغير آمن نسبياً)
2. Momentum على العملات الصاعدة (ربح متوسط)
3. High Risk على عملات صغيرة (ربح كبير - خطر عالي)
4. عرض العملات المتاحة بس

⚠️  لو عايزة تنفذي صفقة حقيقية، قوليلي!
""")

if __name__ == "__main__":
    main()
