"""
🚀 MT5 Copy Trading Integration
النظام بتاعنا للـ Copy Trading على MT5
"""

import MetaTrader5 as mt5
import time
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

class MT5CopyTrader:
    """
    نظام Copy Trading ذكي لـ MT5
    """
    
    def __init__(self, 
                 account: int,
                 password: str,
                 server: str,
                 performance_fee: float = 0.05,  # 5%
                 max_leverage: int = 200):
        """
        تهيئة الاتصال بـ MT5
        
        Args:
            account: رقم الحساب
            password: الباسورد
            server: السيرفر
            performance_fee: نسبة الأرباح (5% افتراضي)
            max_leverage: أقصى رافعة (1:200 افتراضي)
        """
        self.account = account
        self.password = password
        self.server = server
        self.performance_fee = performance_fee
        self.max_leverage = max_leverage
        self.connected = False
        
    def connect(self) -> bool:
        """
        اتصال بـ MT5
        """
        if not mt5.initialize():
            print("❌ فشل تهيئة MT5")
            return False

        authorized = mt5.login(
            login=self.account,
            password=self.password,
            server=self.server
        )

        if not authorized:
            print(f"❌ فشل تسجيل الدخول: {mt5.last_error()}")
            mt5.shutdown()
            return False

        self.connected = True
        print(f"✅ تم الاتصال بحساب: {self.account}")

        # تفعيل التداول الآلي
        if not self._enable_auto_trading():
            print("⚠️ تحذير: التداول الآلي قد يكون معطّل")

        return True

    def _enable_auto_trading(self) -> bool:
        """
        محاولة تفعيل التداول الآلي
        """
        try:
            # فحص حالة Terminal
            terminal = mt5.terminal_info()
            if terminal is None:
                return False

            # فحص السماحيات
            if not terminal.trade_allowed:
                print("❌ التداول معطّل في Terminal - روح Tools > Options > Expert Advisors")
                print("   ✅ فعّل: Allow automated trading")
                return False

            if not terminal.mqid:
                print("⚠️ مش مسجل دخول لـ MQL5 Community")

            return terminal.trade_allowed

        except Exception as e:
            print(f"⚠️ خطأ في فحص Terminal: {e}")
            return False
        
    def get_account_info(self) -> dict:
        """
        معلومات الحساب
        """
        if not self.connected:
            return {}
            
        account_info = mt5.account_info()
        if account_info is None:
            return {}
            
        return {
            'balance': account_info.balance,
            'equity': account_info.equity,
            'profit': account_info.profit,
            'margin': account_info.margin,
            'margin_free': account_info.margin_free,
            'leverage': account_info.leverage
        }
        
    def open_trade(self, 
                   symbol: str,
                   order_type: str,  # 'buy' or 'sell'
                   volume: float,
                   sl: float = 0,
                   tp: float = 0,
                   comment: str = "AI Copy Trade") -> dict:
        """
        فتح صفقة
        
        Args:
            symbol: العملة (مثلاً EURUSD)
            order_type: نوع الأمر ('buy' أو 'sell')
            volume: الحجم (لوت)
            sl: وقف الخسارة
            tp: جني الأرباح
            comment: تعليق
        """
        if not self.connected:
            return {'success': False, 'error': 'غير متصل'}
            
        # تحويل النوع
        if order_type.lower() == 'buy':
            order_type_mt5 = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask
        else:
            order_type_mt5 = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
            
        # فحص التداول على السيمبول
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return {'success': False, 'error': f'السيمبول {symbol} مش موجود'}

        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                return {'success': False, 'error': f'فشل تفعيل {symbol}'}

        if not symbol_info.trade_mode:
            return {'success': False, 'error': f'التداول معطّل على {symbol}'}

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type_mt5,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            error_msg = f'فشل فتح الصفقة: {result.comment} (Code: {result.retcode})'

            # إضافة حلول حسب نوع الخطأ
            if result.retcode == 133:  # TRADE_DISABLED
                error_msg += "\n💡 الحل: افتح MT5 > Tools > Options > Expert Advisors"
                error_msg += "\n   ✅ فعّل: Allow automated trading"
            elif result.retcode == 134:  # MARKET_CLOSED
                error_msg += "\n💡 السوق مقفول دلوقتي"
            elif result.retcode == 10015:  # INVALID_VOLUME
                error_msg += f"\n💡 الحجم {volume} غلط - أقل حجم: {symbol_info.volume_min}"

            return {
                'success': False,
                'error': error_msg,
                'retcode': result.retcode
            }
            
        return {
            'success': True,
            'ticket': result.order,
            'volume': volume,
            'price': result.price,
            'symbol': symbol,
            'type': order_type
        }
        
    def close_trade(self, ticket: int) -> dict:
        """
        إغلاق صفقة
        """
        if not self.connected:
            return {'success': False, 'error': 'غير متصل'}
            
        # الحصول على معلومات الصفقة
        position = mt5.positions_get(ticket=ticket)
        if not position:
            return {'success': False, 'error': 'الصفقة غير موجودة'}
            
        position = position[0]
        
        # تحديد نوع الإغلاق (عكس الفتح)
        if position.type == mt5.ORDER_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(position.symbol).bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(position.symbol).ask
            
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": order_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": "AI Close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return {
                'success': False,
                'error': f'فشل إغلاق الصفقة: {result.comment}'
            }
            
        return {
            'success': True,
            'ticket': ticket,
            'profit': result.profit
        }
        
    def get_open_positions(self) -> list:
        """
        الصفقات المفتوحة
        """
        if not self.connected:
            return []
            
        positions = mt5.positions_get()
        if positions is None:
            return []
            
        return [{
            'ticket': pos.ticket,
            'symbol': pos.symbol,
            'type': 'buy' if pos.type == mt5.ORDER_TYPE_BUY else 'sell',
            'volume': pos.volume,
            'price_open': pos.price_open,
            'price_current': pos.price_current,
            'profit': pos.profit,
            'sl': pos.sl,
            'tp': pos.tp
        } for pos in positions]
        
    def calculate_performance_fee(self, profit: float) -> float:
        """
        حساب عمولة الأداء
        """
        return profit * self.performance_fee if profit > 0 else 0
        
    def auto_trade_loop(self, 
                        strategy_func,
                        interval: int = 60,
                        max_trades: int = 10):
        """
        تشغيل التداول التلقائي
        
        Args:
            strategy_func: دالة الاستراتيجية (ترجع قرارات التداول)
            interval: فترة التحديث بالثواني
            max_trades: أقصى عدد صفقات متزامنة
        """
        print(f"🚀 بدء التداول التلقائي...")
        print(f"⏰ فترة التحديث: {interval} ثانية")
        print(f"📊 أقصى صفقات: {max_trades}")
        
        while True:
            try:
                # فحص الصفقات المفتوحة
                open_positions = self.get_open_positions()
                print(f"\n📈 الصفقات المفتوحة: {len(open_positions)}")
                
                # استدعاء الاستراتيجية
                signals = strategy_func(self, open_positions)
                
                # تنفيذ القرارات
                for signal in signals:
                    if signal['action'] == 'open' and len(open_positions) < max_trades:
                        result = self.open_trade(
                            symbol=signal['symbol'],
                            order_type=signal['type'],
                            volume=signal['volume'],
                            sl=signal.get('sl', 0),
                            tp=signal.get('tp', 0)
                        )
                        if result['success']:
                            print(f"✅ فتح صفقة: {signal['symbol']} - {signal['type']}")
                        else:
                            print(f"❌ فشل: {result['error']}")
                            
                    elif signal['action'] == 'close':
                        result = self.close_trade(signal['ticket'])
                        if result['success']:
                            profit = result['profit']
                            fee = self.calculate_performance_fee(profit)
                            print(f"✅ إغلاق صفقة: ربح {profit:.2f} | عمولة {fee:.2f}")
                        else:
                            print(f"❌ فشل: {result['error']}")
                
                # الانتظار
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n⏹️ إيقاف التداول...")
                break
            except Exception as e:
                print(f"⚠️ خطأ: {e}")
                time.sleep(interval)
                
    def disconnect(self):
        """
        قطع الاتصال
        """
        if self.connected:
            mt5.shutdown()
            self.connected = False
            print("👋 تم قطع الاتصال")


def simple_ma_strategy(trader: MT5CopyTrader, open_positions: list) -> list:
    """
    استراتيجية بسيطة: Moving Average Crossover
    """
    signals = []
    
    # مثال: EURUSD
    symbol = "EURUSD"
    
    # الحصول على البيانات (مبسط - يحتاج تحسين)
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 50)
    if rates is None or len(rates) < 50:
        return signals
        
    # حساب MA
    import pandas as pd
    df = pd.DataFrame(rates)
    df['ma_fast'] = df['close'].rolling(10).mean()
    df['ma_slow'] = df['close'].rolling(30).mean()
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # إشارة شراء: MA السريع يعبر فوق البطيء
    if prev['ma_fast'] <= prev['ma_slow'] and last['ma_fast'] > last['ma_slow']:
        if len(open_positions) < 5:
            signals.append({
                'action': 'open',
                'symbol': symbol,
                'type': 'buy',
                'volume': 0.01,
                'sl': last['close'] - 0.0050,
                'tp': last['close'] + 0.0100
            })
            
    # إشارة بيع: MA السريع يعبر تحت البطيء
    elif prev['ma_fast'] >= prev['ma_slow'] and last['ma_fast'] < last['ma_slow']:
        if len(open_positions) < 5:
            signals.append({
                'action': 'open',
                'symbol': symbol,
                'type': 'sell',
                'volume': 0.01,
                'sl': last['close'] + 0.0050,
                'tp': last['close'] - 0.0100
            })
            
    # إغلاق الصفقات الرابحة
    for pos in open_positions:
        if pos['profit'] > 10:  # إغلاق عند ربح 10 دولار
            signals.append({
                'action': 'close',
                'ticket': pos['ticket']
            })
            
    return signals


if __name__ == "__main__":
    """
    تشغيل البوت
    """
    
    # قراءة بيانات الحساب من .env
    MT5_ACCOUNT = int(os.getenv('MT5_ACCOUNT', '0'))
    MT5_PASSWORD = os.getenv('MT5_PASSWORD', '')
    MT5_SERVER = os.getenv('MT5_SERVER', '')
    
    if not MT5_ACCOUNT or not MT5_PASSWORD or not MT5_SERVER:
        print("❌ أضف بيانات MT5 في ملف .env:")
        print("MT5_ACCOUNT=123456")
        print("MT5_PASSWORD=YourPassword")
        print("MT5_SERVER=YourBroker-Server")
        exit(1)
    
    # إنشاء البوت
    trader = MT5CopyTrader(
        account=MT5_ACCOUNT,
        password=MT5_PASSWORD,
        server=MT5_SERVER,
        performance_fee=0.05,  # 5% من الأرباح
        max_leverage=200
    )
    
    # الاتصال
    if not trader.connect():
        exit(1)
        
    # عرض معلومات الحساب
    info = trader.get_account_info()
    print(f"\n💰 معلومات الحساب:")
    print(f"   الرصيد: ${info['balance']:.2f}")
    print(f"   الأرباح الحالية: ${info['profit']:.2f}")
    print(f"   الرافعة: 1:{info['leverage']}")
    
    # تشغيل التداول التلقائي
    try:
        trader.auto_trade_loop(
            strategy_func=simple_ma_strategy,
            interval=60,  # كل دقيقة
            max_trades=10
        )
    finally:
        trader.disconnect()
