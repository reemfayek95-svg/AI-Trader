#!/usr/bin/env python3
"""
🧪 اختبار MT5 بعد حل مشكلة ERR_TRADE_DISABLED
"""

import MetaTrader5 as mt5
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("🔍 فحص اتصال MT5 وصلاحيات التداول\n")
    
    # البيانات
    account = int(os.getenv('MT5_ACCOUNT', '0'))
    password = os.getenv('MT5_PASSWORD', '')
    server = os.getenv('MT5_SERVER', '')
    
    if not account or not password or not server:
        print("❌ أضف بيانات MT5 في .env:")
        print("MT5_ACCOUNT=123456")
        print("MT5_PASSWORD=YourPassword")
        print("MT5_SERVER=BrokerName-Demo")
        return
    
    # 1. تهيئة
    print("1️⃣ تهيئة MT5...")
    if not mt5.initialize():
        print(f"   ❌ فشل: {mt5.last_error()}")
        return
    print("   ✅ تمام")
    
    # 2. تسجيل دخول
    print(f"\n2️⃣ تسجيل دخول للحساب {account}...")
    if not mt5.login(account, password, server):
        print(f"   ❌ فشل: {mt5.last_error()}")
        mt5.shutdown()
        return
    print("   ✅ تمام")
    
    # 3. فحص Terminal
    print("\n3️⃣ فحص صلاحيات Terminal...")
    terminal = mt5.terminal_info()
    if terminal is None:
        print("   ❌ فشل الحصول على معلومات Terminal")
        mt5.shutdown()
        return
    
    print(f"   التداول الآلي: {'✅ مفعّل' if terminal.trade_allowed else '❌ معطّل'}")
    print(f"   Expert Advisors: {'✅ مسموح' if terminal.expert_enabled else '❌ ممنوع'}")
    print(f"   MQL5 Community: {'✅ متصل' if terminal.mqid else '⚠️ غير متصل'}")
    
    if not terminal.trade_allowed:
        print("\n❌ التداول معطّل!")
        print("💡 الحل:")
        print("   1. افتح MT5 > Tools > Options")
        print("   2. تاب Expert Advisors")
        print("   3. فعّل: Allow automated trading")
        print("   4. اضغط OK")
        print("   5. تأكد إن زر AutoTrading في الشريط أخضر 🟢")
        mt5.shutdown()
        return
    
    # 4. فحص الحساب
    print("\n4️⃣ معلومات الحساب...")
    account_info = mt5.account_info()
    if account_info is None:
        print("   ❌ فشل الحصول على معلومات الحساب")
        mt5.shutdown()
        return
    
    print(f"   الاسم: {account_info.name}")
    print(f"   الرصيد: ${account_info.balance:.2f}")
    print(f"   الرافعة: 1:{account_info.leverage}")
    print(f"   نوع: {'Demo' if account_info.trade_mode == 0 else 'Real'}")
    
    # 5. فحص السيمبول
    print("\n5️⃣ فحص EURUSD...")
    symbol = "EURUSD"
    
    # تفعيل السيمبول
    if not mt5.symbol_select(symbol, True):
        print(f"   ❌ فشل تفعيل {symbol}")
        mt5.shutdown()
        return
    
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"   ❌ {symbol} مش موجود")
        mt5.shutdown()
        return
    
    print(f"   السيمبول: {symbol}")
    print(f"   التداول: {'✅ مسموح' if symbol_info.trade_mode else '❌ ممنوع'}")
    print(f"   أقل حجم: {symbol_info.volume_min}")
    print(f"   السعر الحالي: {symbol_info.bid:.5f}")
    
    # 6. محاولة فتح صفقة تجريبية
    print("\n6️⃣ محاولة فتح صفقة تجريبية (0.01 lot)...")
    
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print("   ❌ فشل الحصول على السعر")
        mt5.shutdown()
        return
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_BUY,
        "price": tick.ask,
        "sl": 0,
        "tp": 0,
        "deviation": 20,
        "magic": 999999,
        "comment": "Test Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request)
    
    print(f"   Return Code: {result.retcode}")
    print(f"   Comment: {result.comment}")
    
    # تحليل النتيجة
    if result.retcode == 10009:  # TRADE_RETCODE_DONE
        print("\n✅✅✅ نجح! الصفقة اتفتحت")
        print(f"   Ticket: {result.order}")
        print(f"   السعر: {result.price}")
        
        # إغلاق الصفقة فورًا
        print("\n7️⃣ إغلاق الصفقة التجريبية...")
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": 0.01,
            "type": mt5.ORDER_TYPE_SELL,
            "position": result.order,
            "price": tick.bid,
            "deviation": 20,
            "magic": 999999,
            "comment": "Test Close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        close_result = mt5.order_send(close_request)
        if close_result.retcode == 10009:
            print("   ✅ تم إغلاق الصفقة")
        else:
            print(f"   ⚠️ لم يتم الإغلاق: {close_result.comment}")
        
        print("\n🎉🎉🎉 كل حاجة شغّالة تمام!")
        print("دلوقتي تقدري تشغّلي البوت الأساسي:")
        print("   python3 mt5_copy_trading.py")
        
    elif result.retcode == 133:  # TRADE_DISABLED
        print("\n❌ ERR_TRADE_DISABLED (133)")
        print("💡 الحل:")
        print("   1. افتح MT5")
        print("   2. Tools > Options > Expert Advisors")
        print("   3. فعّل: [✅] Allow automated trading")
        print("   4. OK")
        print("   5. اضغط زر AutoTrading في الشريط (لازم أخضر)")
        
    elif result.retcode == 134:  # MARKET_CLOSED
        print("\n⚠️ السوق مقفول دلوقتي")
        print("💡 السوق يفتح:")
        print("   - الأحد 10 مساءً GMT")
        print("   - يقفل الجمعة 10 مساءً GMT")
        
    elif result.retcode == 10015:  # INVALID_VOLUME
        print(f"\n❌ حجم الصفقة غلط")
        print(f"💡 أقل حجم مسموح: {symbol_info.volume_min}")
        
    elif result.retcode == 10016:  # INVALID_STOPS
        print("\n❌ Stop Loss/Take Profit غلط")
        
    elif result.retcode == 10018:  # MARKET_CLOSED
        print("\n⚠️ السوق مقفول")
        
    else:
        print(f"\n❌ خطأ غير متوقع: {result.retcode}")
        print(f"   التفاصيل: {result.comment}")
    
    # 8. إنهاء
    print("\n8️⃣ إنهاء الاتصال...")
    mt5.shutdown()
    print("   ✅ تمام")
    
    print("\n" + "="*50)
    print("✅ انتهى الاختبار")


if __name__ == "__main__":
    main()
