#!/usr/bin/env python3
"""
🚀 MT5 Bot Runner - تشغيل مستمر 24/7
يشغّل البوت ويعيد تشغيله تلقائياً لو وقف
"""

import os
import time
import signal
import sys
from datetime import datetime
from dotenv import load_dotenv
from mt5_copy_trading import MT5CopyTrader
from telegram_notifier import TelegramNotifier

load_dotenv()

# Global state
bot = None
telegram = TelegramNotifier()
running = True

def signal_handler(sig, frame):
    """
    معالج إشارات الإيقاف (Ctrl+C)
    """
    global running, bot
    print('\n🛑 إيقاف البوت...')
    running = False
    
    if bot:
        bot.disconnect()
    
    telegram.notify_bot_stopped("تم الإيقاف بواسطة المستخدم")
    sys.exit(0)

# تسجيل معالج الإشارات
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def run_bot_continuously():
    """
    تشغيل البوت بشكل مستمر مع إعادة المحاولة
    """
    global bot, running
    
    # قراءة بيانات MT5
    account = int(os.getenv('MT5_ACCOUNT', 0))
    password = os.getenv('MT5_PASSWORD', '')
    server = os.getenv('MT5_SERVER', '')
    
    if not account or not password or not server:
        print("❌ خطأ: حط بيانات MT5 في ملف .env")
        print("MT5_ACCOUNT, MT5_PASSWORD, MT5_SERVER")
        telegram.notify_error("بيانات MT5 ناقصة في .env")
        return
    
    restart_count = 0
    max_restarts = 10  # أقصى عدد إعادات متتالية
    restart_window = 300  # 5 دقائق
    last_restart_time = time.time()
    
    while running:
        try:
            print(f"\n{'='*50}")
            print(f"🚀 بدء تشغيل البوت - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*50}\n")
            
            # إنشاء البوت
            bot = MT5CopyTrader(
                account=account,
                password=password,
                server=server
            )
            
            # الاتصال
            if not bot.connect():
                raise Exception("فشل الاتصال بـ MT5")
            
            print("✅ البوت متصل وشغال!")
            print("⏰ الآن يراقب السوق ويتداول تلقائياً...\n")
            
            # Reset restart counter بعد نجاح الاتصال
            restart_count = 0
            
            # حلقة المراقبة الرئيسية
            while running and bot.connected:
                try:
                    # تنفيذ الاستراتيجية
                    bot.run_strategy()
                    
                    # انتظار دقيقة
                    time.sleep(60)
                    
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f"⚠️ خطأ في الحلقة الرئيسية: {e}")
                    telegram.notify_error(f"خطأ في loop: {str(e)}")
                    time.sleep(10)
            
            # إذا وصلنا هنا، البوت انقطع
            if running:
                print("\n⚠️ البوت انقطع - إعادة محاولة...")
                
        except KeyboardInterrupt:
            raise
            
        except Exception as e:
            print(f"\n❌ خطأ: {e}")
            telegram.notify_error(f"خطأ في البوت: {str(e)}")
            
        finally:
            # تنظيف
            if bot:
                try:
                    bot.disconnect()
                except:
                    pass
                bot = None
        
        if not running:
            break
        
        # التحقق من عدد إعادات التشغيل
        current_time = time.time()
        if current_time - last_restart_time > restart_window:
            # مضى أكثر من 5 دقائق، إعادة تعيين العداد
            restart_count = 0
        
        restart_count += 1
        last_restart_time = current_time
        
        if restart_count >= max_restarts:
            error_msg = f"فشل البوت {max_restarts} مرات خلال {restart_window//60} دقائق. توقف."
            print(f"❌ {error_msg}")
            telegram.notify_error(error_msg)
            break
        
        # انتظار 30 ثانية قبل إعادة المحاولة
        print(f"⏳ إعادة محاولة بعد 30 ثانية... ({restart_count}/{max_restarts})")
        time.sleep(30)
    
    print("\n👋 البوت توقف.")

def main():
    """
    نقطة البداية
    """
    print("""
╔═══════════════════════════════════════╗
║   🤖 MT5 Copy Trading Bot Runner     ║
║   التشغيل المستمر 24/7               ║
╚═══════════════════════════════════════╝
    """)
    
    # فحص Telegram
    if telegram.enabled:
        print("✅ Telegram: مُفعّل")
        telegram.send_message("🔄 <b>البوت Runner بدأ</b>\n\nجاري الاتصال بـ MT5...")
    else:
        print("⚠️ Telegram: غير مُفعّل (اختياري)")
        print("   لتفعيله: حط TELEGRAM_BOT_TOKEN و TELEGRAM_CHAT_ID في .env\n")
    
    # تشغيل البوت
    run_bot_continuously()

if __name__ == "__main__":
    main()
