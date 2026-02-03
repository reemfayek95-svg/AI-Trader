"""
📊 MT5 Trading Dashboard
لوحة تحكم مباشرة لمراقبة البوت
"""

import MetaTrader5 as mt5
import json
import time
from datetime import datetime
from typing import List, Dict
import os


class MT5Dashboard:
    """
    لوحة تحكم لمراقبة التداول المباشر
    """
    
    def __init__(self, trader):
        self.trader = trader
        self.session_start = datetime.now()
        self.initial_balance = 0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0.0
        self.total_commission = 0.0
        self.trades_history = []
        
    def start_session(self):
        """
        بدء جلسة تداول جديدة
        """
        if self.trader.connected:
            info = self.trader.get_account_info()
            self.initial_balance = info['balance']
            self.session_start = datetime.now()
            print(f"🟢 بدء الجلسة: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"💰 الرصيد الأولي: ${self.initial_balance:.2f}")
            
    def log_trade(self, trade_result: Dict):
        """
        تسجيل صفقة
        """
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            'action': trade_result.get('action', 'unknown'),
            'success': trade_result.get('success', False),
            'profit': trade_result.get('profit', 0.0),
            'symbol': trade_result.get('symbol', ''),
            'type': trade_result.get('type', ''),
            'volume': trade_result.get('volume', 0.0),
            'reason': trade_result.get('reason', '')
        }
        
        self.trades_history.append(trade_record)
        
        # تحديث الإحصائيات
        if trade_result.get('action') == 'close' and trade_result.get('success'):
            self.total_trades += 1
            profit = trade_result.get('profit', 0.0)
            
            if profit > 0:
                self.winning_trades += 1
            else:
                self.losing_trades += 1
                
            self.total_profit += profit
            commission = self.trader.calculate_performance_fee(profit)
            self.total_commission += commission
            
    def print_summary(self):
        """
        طباعة ملخص الجلسة
        """
        os.system('clear' if os.name == 'posix' else 'cls')
        
        duration = datetime.now() - self.session_start
        hours = duration.total_seconds() / 3600
        
        current_info = self.trader.get_account_info()
        current_balance = current_info['balance']
        current_equity = current_info['equity']
        current_profit = current_info['profit']
        
        session_profit = current_balance - self.initial_balance
        roi = (session_profit / self.initial_balance * 100) if self.initial_balance > 0 else 0
        
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        print("=" * 70)
        print("📊 MT5 COPY TRADING DASHBOARD")
        print("=" * 70)
        print()
        
        print(f"⏰ وقت الجلسة: {hours:.1f} ساعة")
        print(f"📅 البداية: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        print("💰 معلومات الحساب:")
        print(f"   الرصيد الأولي:    ${self.initial_balance:>12,.2f}")
        print(f"   الرصيد الحالي:    ${current_balance:>12,.2f}")
        print(f"   القيمة الصافية:   ${current_equity:>12,.2f}")
        print(f"   أرباح مفتوحة:     ${current_profit:>12,.2f}")
        print()
        
        print("📈 أداء الجلسة:")
        print(f"   صافي الربح:       ${session_profit:>12,.2f}")
        profit_emoji = "🟢" if session_profit >= 0 else "🔴"
        print(f"   العائد:            {profit_emoji} {roi:>11.2f}%")
        print(f"   عمولة الأداء:     ${self.total_commission:>12,.2f}")
        print()
        
        print("📊 إحصائيات التداول:")
        print(f"   إجمالي الصفقات:   {self.total_trades:>12}")
        print(f"   صفقات رابحة:      {self.winning_trades:>12} 🟢")
        print(f"   صفقات خاسرة:      {self.losing_trades:>12} 🔴")
        print(f"   نسبة النجاح:      {win_rate:>11.1f}%")
        print()
        
        # الصفقات المفتوحة
        open_positions = self.trader.get_open_positions()
        print(f"🔓 الصفقات المفتوحة ({len(open_positions)}):")
        
        if open_positions:
            print(f"{'الرمز':<10} {'النوع':<6} {'الحجم':<8} {'السعر':<10} {'الربح':<12}")
            print("-" * 70)
            for pos in open_positions:
                profit_emoji = "🟢" if pos['profit'] >= 0 else "🔴"
                print(f"{pos['symbol']:<10} {pos['type']:<6} {pos['volume']:<8.2f} "
                      f"{pos['price_current']:<10.5f} {profit_emoji} ${pos['profit']:>10.2f}")
        else:
            print("   لا توجد صفقات مفتوحة")
            
        print()
        print("=" * 70)
        print(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
    def save_session_report(self, filename: str = None):
        """
        حفظ تقرير الجلسة
        """
        if filename is None:
            filename = f"mt5_session_{self.session_start.strftime('%Y%m%d_%H%M%S')}.json"
            
        current_info = self.trader.get_account_info()
        
        report = {
            'session_info': {
                'start_time': self.session_start.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_hours': (datetime.now() - self.session_start).total_seconds() / 3600
            },
            'account_info': {
                'initial_balance': self.initial_balance,
                'final_balance': current_info['balance'],
                'final_equity': current_info['equity'],
                'session_profit': current_info['balance'] - self.initial_balance,
                'roi_percent': ((current_info['balance'] - self.initial_balance) / self.initial_balance * 100) if self.initial_balance > 0 else 0
            },
            'trading_stats': {
                'total_trades': self.total_trades,
                'winning_trades': self.winning_trades,
                'losing_trades': self.losing_trades,
                'win_rate': (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0,
                'total_profit': self.total_profit,
                'total_commission': self.total_commission
            },
            'trades_history': self.trades_history
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"💾 تم حفظ التقرير: {filename}")
        return filename


def monitored_trading_loop(trader, strategy_func, interval=60, max_trades=10):
    """
    حلقة تداول مع مراقبة مباشرة
    """
    dashboard = MT5Dashboard(trader)
    dashboard.start_session()
    
    print("\n🚀 بدء التداول مع المراقبة المباشرة...")
    print("📊 سيتم تحديث اللوحة كل دقيقة")
    print("⏸️  اضغط Ctrl+C للإيقاف وحفظ التقرير\n")
    
    time.sleep(3)
    
    try:
        while True:
            # الحصول على الصفقات المفتوحة
            open_positions = trader.get_open_positions()
            
            # استدعاء الاستراتيجية
            signals = strategy_func(trader, open_positions)
            
            # تنفيذ الإشارات
            for signal in signals:
                if signal['action'] == 'open' and len(open_positions) < max_trades:
                    result = trader.open_trade(
                        symbol=signal['symbol'],
                        order_type=signal['type'],
                        volume=signal['volume'],
                        sl=signal.get('sl', 0),
                        tp=signal.get('tp', 0),
                        comment=signal.get('reason', 'AI Trade')
                    )
                    
                    result['action'] = 'open'
                    result['reason'] = signal.get('reason', '')
                    dashboard.log_trade(result)
                    
                elif signal['action'] == 'close':
                    result = trader.close_trade(signal['ticket'])
                    result['action'] = 'close'
                    result['reason'] = signal.get('reason', '')
                    dashboard.log_trade(result)
                    
            # عرض اللوحة
            dashboard.print_summary()
            
            # الانتظار
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  إيقاف التداول...")
        dashboard.print_summary()
        print()
        
        # حفظ التقرير
        report_file = dashboard.save_session_report()
        print(f"\n✅ تم حفظ تقرير الجلسة: {report_file}")
        print("\n👋 شكراً لاستخدام MT5 Copy Trading Bot!")
        
    except Exception as e:
        print(f"\n⚠️ خطأ: {e}")
        dashboard.save_session_report()
        

if __name__ == "__main__":
    """
    مثال على الاستخدام
    """
    from mt5_copy_trading import MT5CopyTrader
    from mt5_advanced_strategy import get_strategy
    from dotenv import load_dotenv
    
    load_dotenv()
    
    MT5_ACCOUNT = int(os.getenv('MT5_ACCOUNT', '0'))
    MT5_PASSWORD = os.getenv('MT5_PASSWORD', '')
    MT5_SERVER = os.getenv('MT5_SERVER', '')
    
    if not MT5_ACCOUNT:
        print("❌ أضف بيانات MT5 في ملف .env")
        exit(1)
        
    trader = MT5CopyTrader(
        account=MT5_ACCOUNT,
        password=MT5_PASSWORD,
        server=MT5_SERVER
    )
    
    if not trader.connect():
        exit(1)
        
    # اختيار الاستراتيجية
    strategy = get_strategy('trend')
    
    # تشغيل مع اللوحة
    monitored_trading_loop(
        trader=trader,
        strategy_func=strategy,
        interval=60,
        max_trades=10
    )
    
    trader.disconnect()
