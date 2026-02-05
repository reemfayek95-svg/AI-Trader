"""
📲 Telegram Notifier للبوت MT5
إشعارات فورية لكل الصفقات
"""

import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class TelegramNotifier:
    """
    مُرسل إشعارات Telegram
    """
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.enabled = bool(self.bot_token and self.chat_id)
        
        if not self.enabled:
            print("⚠️ Telegram غير مُفعّل - حط TELEGRAM_BOT_TOKEN و TELEGRAM_CHAT_ID في .env")
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        إرسال رسالة للتليجرام
        """
        if not self.enabled:
            return False
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ فشل إرسال Telegram: {e}")
            return False
    
    def notify_trade_opened(self, symbol: str, order_type: str, volume: float, price: float, sl: float, tp: float):
        """
        إشعار فتح صفقة جديدة
        """
        emoji = "🟢" if order_type == "BUY" else "🔴"
        message = f"""
{emoji} <b>صفقة جديدة مفتوحة</b>

📊 السيمبول: <code>{symbol}</code>
📈 النوع: <b>{order_type}</b>
💰 الحجم: <code>{volume}</code> لوت
💵 السعر: <code>{price:.5f}</code>
🛑 Stop Loss: <code>{sl:.5f}</code>
🎯 Take Profit: <code>{tp:.5f}</code>

🕐 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        return self.send_message(message.strip())
    
    def notify_trade_closed(self, symbol: str, order_type: str, profit: float, volume: float, duration: str):
        """
        إشعار إغلاق صفقة
        """
        emoji = "✅" if profit > 0 else "❌"
        profit_text = f"+${profit:.2f}" if profit > 0 else f"${profit:.2f}"
        
        message = f"""
{emoji} <b>صفقة مُغلقة</b>

📊 السيمبول: <code>{symbol}</code>
📈 النوع: <b>{order_type}</b>
💰 الحجم: <code>{volume}</code> لوت
💵 الربح/الخسارة: <b>{profit_text}</b>
⏱️ المدة: {duration}

🕐 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        return self.send_message(message.strip())
    
    def notify_daily_summary(self, trades_count: int, wins: int, losses: int, total_profit: float, balance: float):
        """
        ملخص يومي
        """
        win_rate = (wins / trades_count * 100) if trades_count > 0 else 0
        profit_emoji = "📈" if total_profit > 0 else "📉"
        
        message = f"""
📊 <b>التقرير اليومي</b>

📌 عدد الصفقات: <b>{trades_count}</b>
✅ رابحة: <b>{wins}</b>
❌ خاسرة: <b>{losses}</b>
📊 نسبة الربح: <b>{win_rate:.1f}%</b>

{profit_emoji} صافي الربح: <b>${total_profit:.2f}</b>
💰 الرصيد الحالي: <b>${balance:.2f}</b>

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        return self.send_message(message.strip())
    
    def notify_bot_started(self, account: int, server: str, balance: float):
        """
        إشعار بدء البوت
        """
        message = f"""
🚀 <b>البوت بدأ الشغل!</b>

👤 الحساب: <code>{account}</code>
🌐 السيرفر: <code>{server}</code>
💰 الرصيد: <b>${balance:.2f}</b>

✅ البوت الآن يراقب السوق ويتداول تلقائياً
        """
        return self.send_message(message.strip())
    
    def notify_bot_stopped(self, reason: str = "تم الإيقاف يدوياً"):
        """
        إشعار إيقاف البوت
        """
        message = f"""
🛑 <b>البوت توقف</b>

📝 السبب: {reason}
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        return self.send_message(message.strip())
    
    def notify_error(self, error_message: str):
        """
        إشعار خطأ
        """
        message = f"""
⚠️ <b>خطأ في البوت</b>

❌ الرسالة: <code>{error_message}</code>
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        return self.send_message(message.strip())


# Test
if __name__ == "__main__":
    notifier = TelegramNotifier()
    
    if notifier.enabled:
        print("✅ اختبار Telegram...")
        notifier.send_message("🧪 <b>Test Message</b>\n\nالتليجرام شغال تمام!")
    else:
        print("❌ Telegram غير مُفعّل")
