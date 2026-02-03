#!/bin/bash

echo "🚀 MT5 Copy Trading Bot Launcher"
echo "================================="
echo ""

# فحص ملف .env
if [ ! -f .env ]; then
    echo "❌ ملف .env غير موجود"
    echo "📝 انسخ .env.example وعدّل البيانات:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

# فحص Dependencies
echo "📦 فحص المكتبات المطلوبة..."
pip install -q MetaTrader5 pandas numpy python-dotenv

# عرض الخيارات
echo ""
echo "اختر الاستراتيجية:"
echo "  1. trend       - متابعة الترند (موصى به للمبتدئين)"
echo "  2. scalping    - سكالبينج (صفقات سريعة)"
echo "  3. breakout    - اختراق المستويات"
echo "  4. ml          - تعلم آلي"
echo "  5. simple      - استراتيجية بسيطة (MA فقط)"
echo ""

read -p "رقم الاستراتيجية [1-5]: " choice

case $choice in
    1)
        STRATEGY="trend"
        echo "✅ استراتيجية متابعة الترند"
        ;;
    2)
        STRATEGY="scalping"
        echo "✅ استراتيجية سكالبينج"
        ;;
    3)
        STRATEGY="breakout"
        echo "✅ استراتيجية الاختراق"
        ;;
    4)
        STRATEGY="ml"
        echo "✅ استراتيجية ML"
        ;;
    5)
        STRATEGY="simple"
        echo "✅ استراتيجية بسيطة"
        ;;
    *)
        echo "❌ اختيار غير صحيح"
        exit 1
        ;;
esac

echo ""
echo "🚀 بدء التشغيل..."
echo ""

# تشغيل البوت مع الاستراتيجية المختارة
if [ "$STRATEGY" = "simple" ]; then
    python mt5_copy_trading.py
else
    # إنشاء ملف مؤقت للتشغيل
    cat > /tmp/run_mt5_strategy.py << EOF
import os
from mt5_copy_trading import MT5CopyTrader
from mt5_advanced_strategy import get_strategy
from dotenv import load_dotenv

load_dotenv()

MT5_ACCOUNT = int(os.getenv('MT5_ACCOUNT', '0'))
MT5_PASSWORD = os.getenv('MT5_PASSWORD', '')
MT5_SERVER = os.getenv('MT5_SERVER', '')

if not MT5_ACCOUNT or not MT5_PASSWORD or not MT5_SERVER:
    print("❌ أضف بيانات MT5 في ملف .env")
    exit(1)

trader = MT5CopyTrader(
    account=MT5_ACCOUNT,
    password=MT5_PASSWORD,
    server=MT5_SERVER,
    performance_fee=0.05,
    max_leverage=200
)

if not trader.connect():
    exit(1)

info = trader.get_account_info()
print(f"💰 الرصيد: \${info['balance']:.2f}")
print(f"📊 الأرباح: \${info['profit']:.2f}")
print("")

strategy = get_strategy('$STRATEGY')
if not strategy:
    trader.disconnect()
    exit(1)

print("🔥 بدء التداول التلقائي...")
print("⏸️  اضغط Ctrl+C للإيقاف")
print("")

try:
    trader.auto_trade_loop(
        strategy_func=strategy,
        interval=60,
        max_trades=10
    )
finally:
    trader.disconnect()
EOF

    python /tmp/run_mt5_strategy.py
fi
