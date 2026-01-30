#!/usr/bin/env python3
"""
Auto Trading Bot - $10 USDT Strategy
استراتيجية تداول تلقائية بـ $10
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

TRADE_AMOUNT = 10.0  # $10 USDT

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

def get_orderbook(pair, limit=10):
    """Get order book depth"""
    data = api_request('GET', '/spot/order_book', {'currency_pair': pair, 'limit': limit})
    if data:
        return {
            'bids': [[float(p), float(a)] for p, a in data.get('bids', [])[:5]],
            'asks': [[float(p), float(a)] for p, a in data.get('asks', [])[:5]]
        }
    return None

def place_order(pair, side, amount, price=None):
    """Place order"""
    order_data = {
        'currency_pair': pair,
        'side': side,
        'amount': str(amount),
        'type': 'market' if price is None else 'limit',
        'time_in_force': 'ioc'  # Immediate or cancel
    }
    
    if price:
        order_data['price'] = str(price)
    
    result = api_request('POST', '/spot/orders', data=order_data)
    return result

def find_best_opportunities():
    """Find best trading opportunities"""
    print("\n🔍 جاري البحث عن أفضل الفرص...")
    
    # High volatility pairs with good volume
    pairs = [
        'BTC_USDT', 'ETH_USDT', 'SOL_USDT', 'BNB_USDT',
        'DOGE_USDT', 'SHIB_USDT', 'PEPE_USDT', 'WIF_USDT',
        'BONK_USDT', 'FLOKI_USDT', 'MATIC_USDT', 'AVAX_USDT'
    ]
    
    opportunities = []
    
    for pair in pairs:
        ticker = get_ticker(pair)
        if ticker and ticker['volume'] > 1000:  # Good volume
            # Calculate volatility score
            volatility = abs(ticker['change'])
            spread = ((ticker['high'] - ticker['low']) / ticker['last']) * 100
            
            score = volatility * 0.6 + spread * 0.4
            
            opportunities.append({
                'pair': pair,
                'price': ticker['last'],
                'change': ticker['change'],
                'volatility': volatility,
                'spread': spread,
                'score': score,
                'volume': ticker['volume']
            })
    
    # Sort by score
    opportunities.sort(key=lambda x: x['score'], reverse=True)
    
    return opportunities[:5]

def execute_scalping_strategy(pair, amount_usdt):
    """Execute scalping strategy"""
    print(f"\n🎯 تنفيذ استراتيجية Scalping على {pair}")
    print(f"💰 المبلغ: ${amount_usdt} USDT")
    
    ticker = get_ticker(pair)
    if not ticker:
        print("❌ فشل الحصول على السعر")
        return False
    
    current_price = ticker['last']
    
    # Calculate buy amount
    buy_amount = amount_usdt / current_price
    
    # Target profit: 2-3%
    target_profit = 0.025  # 2.5%
    sell_price = current_price * (1 + target_profit)
    
    # Stop loss: 1%
    stop_loss = 0.01
    stop_price = current_price * (1 - stop_loss)
    
    print(f"\n📊 تفاصيل الصفقة:")
    print(f"   السعر الحالي: ${current_price:.8f}")
    print(f"   الكمية: {buy_amount:.8f}")
    print(f"   هدف البيع: ${sell_price:.8f} (+2.5%)")
    print(f"   وقف الخسارة: ${stop_price:.8f} (-1%)")
    
    print(f"\n⚠️  هل تريدين تنفيذ الصفقة؟")
    print(f"   الربح المتوقع: ${amount_usdt * target_profit:.2f}")
    print(f"   الخسارة القصوى: ${amount_usdt * stop_loss:.2f}")
    
    return {
        'pair': pair,
        'buy_price': current_price,
        'buy_amount': buy_amount,
        'sell_price': sell_price,
        'stop_price': stop_price,
        'amount_usdt': amount_usdt
    }

def main():
    print("=" * 60)
    print("🚀 Auto Trading Bot - $10 Strategy")
    print("=" * 60)
    
    # Check balance
    balance = get_balance()
    usdt_balance = balance.get('USDT', 0)
    
    print(f"\n💰 رصيدك: ${usdt_balance:.2f} USDT")
    
    if usdt_balance < TRADE_AMOUNT:
        print(f"\n❌ رصيدك أقل من ${TRADE_AMOUNT}")
        print(f"   محتاج على الأقل ${TRADE_AMOUNT} USDT")
        return
    
    # Find opportunities
    opportunities = find_best_opportunities()
    
    print("\n🔥 أفضل 5 فرص للتداول:")
    print("=" * 60)
    
    for i, opp in enumerate(opportunities, 1):
        print(f"\n{i}. {opp['pair']}:")
        print(f"   السعر: ${opp['price']:.8f}")
        print(f"   التغير 24h: {opp['change']:.2f}%")
        print(f"   التقلب: {opp['volatility']:.2f}%")
        print(f"   النطاق: {opp['spread']:.2f}%")
        print(f"   النقاط: {opp['score']:.2f}")
    
    # Best opportunity
    best = opportunities[0]
    
    print("\n" + "=" * 60)
    print(f"🎯 أفضل فرصة: {best['pair']}")
    print("=" * 60)
    
    # Execute strategy
    trade_plan = execute_scalping_strategy(best['pair'], TRADE_AMOUNT)
    
    print("\n" + "=" * 60)
    print("📋 خطة التداول جاهزة!")
    print("=" * 60)
    
    print(f"""
🎯 الاستراتيجية: Scalping
💰 المبلغ: ${TRADE_AMOUNT} USDT
📈 العملة: {trade_plan['pair']}

📊 التفاصيل:
   - شراء: {trade_plan['buy_amount']:.8f} @ ${trade_plan['buy_price']:.8f}
   - بيع: @ ${trade_plan['sell_price']:.8f} (+2.5%)
   - وقف خسارة: @ ${trade_plan['stop_price']:.8f} (-1%)

💵 النتائج المتوقعة:
   ✅ ربح: ${trade_plan['amount_usdt'] * 0.025:.2f} (+2.5%)
   ❌ خسارة: ${trade_plan['amount_usdt'] * 0.01:.2f} (-1%)

⏱️  مدة الصفقة المتوقعة: 5-30 دقيقة

⚠️  لتنفيذ الصفقة:
   قولي "نفذ" أو "execute"
   
💡 نصيحة:
   - راقبي السوق كل 5 دقائق
   - لو وصل الهدف، بيع فوراً
   - لو وصل Stop Loss، بيع فوراً
   - ما تطمعيش!
""")
    
    # Save trade plan
    with open('trade_plan.json', 'w') as f:
        json.dump(trade_plan, f, indent=2)
    
    print("💾 خطة التداول محفوظة في: trade_plan.json")

if __name__ == "__main__":
    main()
