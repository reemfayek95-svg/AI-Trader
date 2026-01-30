#!/bin/bash
echo "🤖 Gate.io Trading Bot"
echo "====================="
echo ""
echo "اختاري:"
echo "1. البوت البسيط (عرض الأسعار والرصيد)"
echo "2. البوت الذكي (AI Trading)"
echo "3. اختبار الاتصال"
echo "4. شوف رصيدك بسرعة"
echo ""
read -p "اختاري (1-4): " choice

case $choice in
  1)
    echo ""
    echo "🚀 تشغيل البوت البسيط..."
    python3 gate_trader_simple.py
    ;;
  2)
    echo ""
    echo "🤖 تشغيل البوت الذكي..."
    python3 run_gate_trader.py
    ;;
  3)
    echo ""
    echo "🔧 اختبار الاتصال..."
    python3 test_gate_connection.py
    ;;
  4)
    echo ""
    echo "💰 رصيدك:"
    python3 -c "
import time, hmac, hashlib, requests
API_KEY = '465edd938a57d272184fcdd8c4cbdd20'
API_SECRET = '3dda9877d956de7bfa41aa65db4a60205b5abdca33c4aeea1d9a450782d543f3'
def gen_sign(method, url, query_string='', payload_string=''):
    t = str(int(time.time()))
    m = hashlib.sha512()
    m.update((payload_string or '').encode('utf-8'))
    hashed_payload = m.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string, hashed_payload, t)
    sign = hmac.new(API_SECRET.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': API_KEY, 'Timestamp': t, 'SIGN': sign}
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
sign_headers = gen_sign('GET', '/api/v4/spot/accounts', '', '')
headers.update(sign_headers)
r = requests.get('https://api.gateio.ws/api/v4/spot/accounts', headers=headers)
data = r.json()
for item in data:
    if float(item.get('available', 0)) > 0:
        print(f\"  {item['currency']}: {float(item['available']):.8f}\")
"
    ;;
  *)
    echo "❌ اختيار غلط"
    ;;
esac
