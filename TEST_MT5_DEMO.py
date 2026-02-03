"""
🧪 اختبار سريع لـ MT5 على حساب Demo
تشغيل تجريبي بدون مخاطرة
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_mt5_connection():
    """
    اختبار الاتصال بـ MT5
    """
    try:
        import MetaTrader5 as mt5
        print("✅ مكتبة MT5 مثبتة")
    except ImportError:
        print("❌ مكتبة MT5 غير مثبتة")
        print("تثبيت: pip install MetaTrader5")
        return False
        
    # قراءة البيانات
    account = os.getenv('MT5_ACCOUNT')
    password = os.getenv('MT5_PASSWORD')
    server = os.getenv('MT5_SERVER')
    
    if not account or not password or not server:
        print("❌ بيانات MT5 غير موجودة في .env")
        print("أضف:")
        print("  MT5_ACCOUNT=123456")
        print("  MT5_PASSWORD=YourPass")
        print("  MT5_SERVER=Broker-Server")
        return False
        
    print(f"📝 الحساب: {account}")
    print(f"📝 السيرفر: {server}")
    
    # محاولة الاتصال
    if not mt5.initialize():
        print("❌ فشل تهيئة MT5")
        print("تأكد من تشغيل MT5 على جهازك")
        return False
        
    print("✅ تم تهيئة MT5")
    
    # تسجيل الدخول
    authorized = mt5.login(
        login=int(account),
        password=password,
        server=server
    )
    
    if not authorized:
        print(f"❌ فشل تسجيل الدخول: {mt5.last_error()}")
        print("تحقق من البيانات في .env")
        mt5.shutdown()
        return False
        
    print("✅ تم تسجيل الدخول بنجاح!")
    
    # معلومات الحساب
    account_info = mt5.account_info()
    print("\n💰 معلومات الحساب:")
    print(f"   الرصيد: ${account_info.balance:.2f}")
    print(f"   الأرباح: ${account_info.profit:.2f}")
    print(f"   الرافعة: 1:{account_info.leverage}")
    print(f"   العملة: {account_info.currency}")
    
    # اختبار قراءة سعر
    symbol = "EURUSD"
    tick = mt5.symbol_info_tick(symbol)
    
    if tick:
        print(f"\n📊 سعر {symbol}:")
        print(f"   Bid: {tick.bid}")
        print(f"   Ask: {tick.ask}")
        print(f"   Spread: {(tick.ask - tick.bid) * 10000:.1f} pips")
    else:
        print(f"\n⚠️ لم يتم العثور على {symbol}")
        
    mt5.shutdown()
    print("\n✅ الاختبار ناجح! جاهز للتشغيل")
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("🧪 اختبار MT5 Copy Trading Bot")
    print("=" * 50)
    print()
    
    if test_mt5_connection():
        print("\n" + "=" * 50)
        print("🚀 لتشغيل البوت:")
        print("   bash RUN_MT5_BOT.sh")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ فشل الاختبار - راجع الأخطاء أعلاه")
        print("=" * 50)
