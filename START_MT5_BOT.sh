#!/bin/bash

echo "╔═══════════════════════════════════════╗"
echo "║   🚀 MT5 Bot - Quick Start           ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# التحقق من الملفات المطلوبة
if [ ! -f ".env" ]; then
    echo "❌ ملف .env مش موجود!"
    echo ""
    echo "📝 الحل:"
    echo "1. انسخي .env.example إلى .env:"
    echo "   cp .env.example .env"
    echo ""
    echo "2. افتحي .env وحطي بيانات MT5:"
    echo "   MT5_ACCOUNT=رقم_الحساب"
    echo "   MT5_PASSWORD=الباسورد"
    echo "   MT5_SERVER=اسم_السيرفر"
    echo ""
    echo "3. (اختياري) حطي بيانات Telegram للإشعارات:"
    echo "   TELEGRAM_BOT_TOKEN=xxx"
    echo "   TELEGRAM_CHAT_ID=xxx"
    echo ""
    exit 1
fi

# التحقق من تثبيت المكتبات
echo "🔍 فحص المتطلبات..."
python3 -c "import MetaTrader5" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ مكتبة MetaTrader5 غير مثبتة!"
    echo ""
    echo "📦 التثبيت:"
    echo "pip install MetaTrader5 python-dotenv requests"
    echo ""
    exit 1
fi

echo "✅ جميع المتطلبات موجودة"
echo ""

# عرض الخيارات
echo "اختاري وضع التشغيل:"
echo ""
echo "1️⃣  تشغيل عادي (مع لوج في Terminal)"
echo "2️⃣  تشغيل في Background (يشتغل لوحده)"
echo "3️⃣  اختبار الاتصال فقط"
echo "4️⃣  اختبار Telegram"
echo ""
read -p "الاختيار (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚀 تشغيل البوت..."
        echo "⚠️ اضغطي Ctrl+C للإيقاف"
        echo ""
        python3 mt5_bot_runner.py
        ;;
    2)
        echo ""
        echo "🚀 تشغيل البوت في Background..."
        nohup python3 mt5_bot_runner.py > mt5_bot.log 2>&1 &
        BOT_PID=$!
        echo "✅ البوت شغال! PID: $BOT_PID"
        echo ""
        echo "📝 للمراقبة:"
        echo "   tail -f mt5_bot.log"
        echo ""
        echo "🛑 للإيقاف:"
        echo "   kill $BOT_PID"
        echo ""
        echo "أو استخدمي:"
        echo "   pkill -f mt5_bot_runner.py"
        ;;
    3)
        echo ""
        echo "🧪 اختبار الاتصال..."
        python3 << 'PYEOF'
import os
from dotenv import load_dotenv
import MetaTrader5 as mt5

load_dotenv()

account = int(os.getenv('MT5_ACCOUNT', 0))
password = os.getenv('MT5_PASSWORD', '')
server = os.getenv('MT5_SERVER', '')

if not account or not password or not server:
    print("❌ بيانات MT5 ناقصة في .env!")
    exit(1)

print(f"🔗 الاتصال بـ MT5...")
print(f"   الحساب: {account}")
print(f"   السيرفر: {server}")

if not mt5.initialize():
    print("❌ فشل تهيئة MT5")
    exit(1)

if not mt5.login(account, password, server):
    print(f"❌ فشل تسجيل الدخول: {mt5.last_error()}")
    mt5.shutdown()
    exit(1)

print("✅ الاتصال نجح!")

info = mt5.account_info()
if info:
    print(f"\n💰 معلومات الحساب:")
    print(f"   الرصيد: ${info.balance:.2f}")
    print(f"   الربح العائم: ${info.profit:.2f}")
    print(f"   الرافعة: 1:{info.leverage}")

mt5.shutdown()
PYEOF
        ;;
    4)
        echo ""
        echo "📲 اختبار Telegram..."
        python3 telegram_notifier.py
        ;;
    *)
        echo "❌ اختيار غير صحيح!"
        exit 1
        ;;
esac
