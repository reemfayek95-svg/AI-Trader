"""
🔥 استراتيجيات متقدمة للـ Copy Trading
استراتيجيات جاهزة للاستخدام مع نظام MT5
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json


class TrendFollowingStrategy:
    """
    استراتيجية متابعة الترند - مناسبة للأسواق الترندية
    تستخدم: MA, RSI, ATR
    """
    
    def __init__(self, 
                 symbols=['EURUSD', 'GBPUSD', 'USDJPY'],
                 timeframe=mt5.TIMEFRAME_M15,
                 risk_percent=0.02):
        self.symbols = symbols
        self.timeframe = timeframe
        self.risk_percent = risk_percent
        
    def analyze(self, trader, open_positions):
        """
        تحليل وإصدار الإشارات
        """
        signals = []
        
        for symbol in self.symbols:
            # الحصول على البيانات
            rates = mt5.copy_rates_from_pos(symbol, self.timeframe, 0, 100)
            if rates is None or len(rates) < 100:
                continue
                
            df = pd.DataFrame(rates)
            
            # حساب المؤشرات
            df['ma_20'] = df['close'].rolling(20).mean()
            df['ma_50'] = df['close'].rolling(50).mean()
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # ATR
            df['h-l'] = df['high'] - df['low']
            df['h-c'] = abs(df['high'] - df['close'].shift())
            df['l-c'] = abs(df['low'] - df['close'].shift())
            df['tr'] = df[['h-l', 'h-c', 'l-c']].max(axis=1)
            df['atr'] = df['tr'].rolling(14).mean()
            
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            # شرط الشراء
            if (last['ma_20'] > last['ma_50'] and 
                last['rsi'] > 50 and last['rsi'] < 70 and
                prev['close'] < prev['ma_20'] and 
                last['close'] > last['ma_20']):
                
                # فحص عدم وجود صفقة مفتوحة لنفس الرمز
                has_position = any(p['symbol'] == symbol for p in open_positions)
                if not has_position:
                    # حساب حجم الصفقة
                    account_info = trader.get_account_info()
                    risk_amount = account_info['balance'] * self.risk_percent
                    
                    # SL & TP
                    sl = last['close'] - (2 * last['atr'])
                    tp = last['close'] + (3 * last['atr'])
                    
                    # حساب الحجم
                    pip_value = 10  # تقريبي لـ standard lot
                    volume = round(risk_amount / (abs(last['close'] - sl) * pip_value), 2)
                    volume = max(0.01, min(volume, 1.0))  # بين 0.01 و 1.0
                    
                    signals.append({
                        'action': 'open',
                        'symbol': symbol,
                        'type': 'buy',
                        'volume': volume,
                        'sl': sl,
                        'tp': tp,
                        'reason': f'Trend BUY: MA cross + RSI {last["rsi"]:.1f}'
                    })
                    
            # شرط البيع
            elif (last['ma_20'] < last['ma_50'] and 
                  last['rsi'] < 50 and last['rsi'] > 30 and
                  prev['close'] > prev['ma_20'] and 
                  last['close'] < last['ma_20']):
                
                has_position = any(p['symbol'] == symbol for p in open_positions)
                if not has_position:
                    account_info = trader.get_account_info()
                    risk_amount = account_info['balance'] * self.risk_percent
                    
                    sl = last['close'] + (2 * last['atr'])
                    tp = last['close'] - (3 * last['atr'])
                    
                    pip_value = 10
                    volume = round(risk_amount / (abs(last['close'] - sl) * pip_value), 2)
                    volume = max(0.01, min(volume, 1.0))
                    
                    signals.append({
                        'action': 'open',
                        'symbol': symbol,
                        'type': 'sell',
                        'volume': volume,
                        'sl': sl,
                        'tp': tp,
                        'reason': f'Trend SELL: MA cross + RSI {last["rsi"]:.1f}'
                    })
                    
        # إدارة الصفقات المفتوحة
        for pos in open_positions:
            # Trailing Stop
            if pos['profit'] > 20:  # إذا ربح أكثر من 20 دولار
                signals.append({
                    'action': 'close',
                    'ticket': pos['ticket'],
                    'reason': f'Trailing Stop: Profit ${pos["profit"]:.2f}'
                })
                
        return signals


class ScalpingStrategy:
    """
    استراتيجية سكالبينج - صفقات سريعة
    تستخدم: Bollinger Bands, MACD
    """
    
    def __init__(self, 
                 symbols=['EURUSD', 'GBPUSD'],
                 timeframe=mt5.TIMEFRAME_M5,
                 risk_percent=0.01):
        self.symbols = symbols
        self.timeframe = timeframe
        self.risk_percent = risk_percent
        
    def analyze(self, trader, open_positions):
        """
        تحليل سكالبينج
        """
        signals = []
        
        for symbol in self.symbols:
            rates = mt5.copy_rates_from_pos(symbol, self.timeframe, 0, 50)
            if rates is None or len(rates) < 50:
                continue
                
            df = pd.DataFrame(rates)
            
            # Bollinger Bands
            df['sma'] = df['close'].rolling(20).mean()
            df['std'] = df['close'].rolling(20).std()
            df['bb_upper'] = df['sma'] + (2 * df['std'])
            df['bb_lower'] = df['sma'] - (2 * df['std'])
            
            # MACD
            ema_12 = df['close'].ewm(span=12).mean()
            ema_26 = df['close'].ewm(span=26).mean()
            df['macd'] = ema_12 - ema_26
            df['signal'] = df['macd'].ewm(span=9).mean()
            
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Scalp BUY
            if (last['close'] < last['bb_lower'] and 
                last['macd'] > last['signal'] and
                prev['macd'] <= prev['signal']):
                
                has_position = any(p['symbol'] == symbol for p in open_positions)
                if not has_position:
                    tick = mt5.symbol_info_tick(symbol)
                    spread = tick.ask - tick.bid
                    
                    signals.append({
                        'action': 'open',
                        'symbol': symbol,
                        'type': 'buy',
                        'volume': 0.01,
                        'sl': last['close'] - 0.0020,
                        'tp': last['close'] + 0.0030,
                        'reason': f'Scalp BUY: BB oversold + MACD cross'
                    })
                    
            # Scalp SELL
            elif (last['close'] > last['bb_upper'] and 
                  last['macd'] < last['signal'] and
                  prev['macd'] >= prev['signal']):
                
                has_position = any(p['symbol'] == symbol for p in open_positions)
                if not has_position:
                    signals.append({
                        'action': 'open',
                        'symbol': symbol,
                        'type': 'sell',
                        'volume': 0.01,
                        'sl': last['close'] + 0.0020,
                        'tp': last['close'] - 0.0030,
                        'reason': f'Scalp SELL: BB overbought + MACD cross'
                    })
                    
        # إغلاق سريع للسكالبينج
        for pos in open_positions:
            if pos['profit'] > 5 or pos['profit'] < -3:
                signals.append({
                    'action': 'close',
                    'ticket': pos['ticket'],
                    'reason': f'Scalp Exit: P/L ${pos["profit"]:.2f}'
                })
                
        return signals


class BreakoutStrategy:
    """
    استراتيجية الاختراق - تداول كسر المستويات
    """
    
    def __init__(self, 
                 symbols=['EURUSD', 'XAUUSD'],
                 timeframe=mt5.TIMEFRAME_H1,
                 risk_percent=0.025):
        self.symbols = symbols
        self.timeframe = timeframe
        self.risk_percent = risk_percent
        
    def analyze(self, trader, open_positions):
        """
        كشف الاختراقات
        """
        signals = []
        
        for symbol in self.symbols:
            rates = mt5.copy_rates_from_pos(symbol, self.timeframe, 0, 50)
            if rates is None or len(rates) < 50:
                continue
                
            df = pd.DataFrame(rates)
            
            # حساب مستويات الدعم والمقاومة
            lookback = 20
            df['resistance'] = df['high'].rolling(lookback).max()
            df['support'] = df['low'].rolling(lookback).min()
            
            # ATR للتقلب
            df['h-l'] = df['high'] - df['low']
            df['h-c'] = abs(df['high'] - df['close'].shift())
            df['l-c'] = abs(df['low'] - df['close'].shift())
            df['tr'] = df[['h-l', 'h-c', 'l-c']].max(axis=1)
            df['atr'] = df['tr'].rolling(14).mean()
            
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            # اختراق المقاومة
            if prev['close'] <= prev['resistance'] and last['close'] > last['resistance']:
                has_position = any(p['symbol'] == symbol for p in open_positions)
                if not has_position:
                    account_info = trader.get_account_info()
                    risk = account_info['balance'] * self.risk_percent
                    
                    sl = last['resistance'] - last['atr']
                    tp = last['close'] + (2 * last['atr'])
                    
                    volume = 0.01  # مبسط
                    
                    signals.append({
                        'action': 'open',
                        'symbol': symbol,
                        'type': 'buy',
                        'volume': volume,
                        'sl': sl,
                        'tp': tp,
                        'reason': f'Breakout BUY: Resistance broken at {last["resistance"]:.5f}'
                    })
                    
            # اختراق الدعم
            elif prev['close'] >= prev['support'] and last['close'] < last['support']:
                has_position = any(p['symbol'] == symbol for p in open_positions)
                if not has_position:
                    account_info = trader.get_account_info()
                    risk = account_info['balance'] * self.risk_percent
                    
                    sl = last['support'] + last['atr']
                    tp = last['close'] - (2 * last['atr'])
                    
                    volume = 0.01
                    
                    signals.append({
                        'action': 'open',
                        'symbol': symbol,
                        'type': 'sell',
                        'volume': volume,
                        'sl': sl,
                        'tp': tp,
                        'reason': f'Breakout SELL: Support broken at {last["support"]:.5f}'
                    })
                    
        return signals


class AIMLStrategy:
    """
    استراتيجية ML بسيطة - تستخدم البيانات التاريخية للتنبؤ
    """
    
    def __init__(self, symbols=['EURUSD']):
        self.symbols = symbols
        self.model_trained = False
        
    def train_simple_model(self, df):
        """
        تدريب نموذج بسيط (تصنيف: صعود/هبوط)
        """
        # تحضير Features
        df['return'] = df['close'].pct_change()
        df['ma_5'] = df['close'].rolling(5).mean()
        df['ma_10'] = df['close'].rolling(10).mean()
        df['vol'] = df['tick_volume'].rolling(5).mean()
        
        # Target: 1 إذا الشمعة القادمة صاعدة
        df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
        
        df = df.dropna()
        
        # بيانات بسيطة - قرار بسيط
        # إذا MA5 > MA10 -> BUY signal probability higher
        df['signal'] = (df['ma_5'] > df['ma_10']).astype(int)
        
        return df
        
    def analyze(self, trader, open_positions):
        """
        ML Trading
        """
        signals = []
        
        for symbol in self.symbols:
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 200)
            if rates is None or len(rates) < 200:
                continue
                
            df = pd.DataFrame(rates)
            df = self.train_simple_model(df)
            
            if len(df) < 10:
                continue
                
            last = df.iloc[-1]
            
            # قرار ML بسيط
            if last['signal'] == 1 and last['return'] > 0:
                has_position = any(p['symbol'] == symbol for p in open_positions)
                if not has_position:
                    signals.append({
                        'action': 'open',
                        'symbol': symbol,
                        'type': 'buy',
                        'volume': 0.01,
                        'sl': last['close'] - 0.0050,
                        'tp': last['close'] + 0.0100,
                        'reason': 'ML Prediction: BUY'
                    })
                    
            elif last['signal'] == 0 and last['return'] < 0:
                has_position = any(p['symbol'] == symbol for p in open_positions)
                if not has_position:
                    signals.append({
                        'action': 'open',
                        'symbol': symbol,
                        'type': 'sell',
                        'volume': 0.01,
                        'sl': last['close'] + 0.0050,
                        'tp': last['close'] - 0.0100,
                        'reason': 'ML Prediction: SELL'
                    })
                    
        return signals


# دالة wrapper للاستخدام مع البوت الرئيسي
def get_strategy(strategy_name: str):
    """
    اختيار الاستراتيجية
    
    Args:
        strategy_name: اسم الاستراتيجية
            - 'trend': متابعة الترند
            - 'scalping': سكالبينج
            - 'breakout': اختراق
            - 'ml': تعلم آلي
    """
    strategies = {
        'trend': TrendFollowingStrategy(),
        'scalping': ScalpingStrategy(),
        'breakout': BreakoutStrategy(),
        'ml': AIMLStrategy()
    }
    
    strategy = strategies.get(strategy_name.lower())
    if not strategy:
        print(f"❌ استراتيجية غير موجودة: {strategy_name}")
        print(f"الاستراتيجيات المتاحة: {list(strategies.keys())}")
        return None
        
    return lambda trader, positions: strategy.analyze(trader, positions)


if __name__ == "__main__":
    print("📊 الاستراتيجيات المتاحة:")
    print("  1. trend - متابعة الترند")
    print("  2. scalping - سكالبينج")
    print("  3. breakout - اختراق المستويات")
    print("  4. ml - تعلم آلي بسيط")
    print("\nاستخدام:")
    print("  from mt5_advanced_strategy import get_strategy")
    print("  strategy = get_strategy('trend')")
    print("  trader.auto_trade_loop(strategy, interval=60)")
