#!/usr/bin/env python3
"""
تحليل أفضل الصفقات وأكبر الأرباح
"""

import json
import os
from pathlib import Path
from datetime import datetime

def analyze_all_trades():
    """تحليل جميع الصفقات من كل الموديلات"""
    
    data_dir = Path("/vercel/sandbox/data/agent_data")
    
    all_trades = []
    
    # Loop through all model directories
    for model_dir in data_dir.iterdir():
        if not model_dir.is_dir():
            continue
            
        model_name = model_dir.name
        
        # Read position file
        position_file = model_dir / "position" / "position.jsonl"
        
        if not position_file.exists():
            continue
            
        print(f"📊 تحليل موديل: {model_name}")
        
        # Read all positions
        positions = []
        with open(position_file, 'r') as f:
            for line in f:
                if line.strip():
                    positions.append(json.loads(line))
        
        # Calculate trades profit/loss
        if len(positions) >= 2:
            initial_cash = positions[0]['positions'].get('CASH', 0)
            
            for i, pos in enumerate(positions):
                date = pos.get('date', 'Unknown')
                cash = pos['positions'].get('CASH', 0)
                holdings = {k: v for k, v in pos['positions'].items() if k != 'CASH'}
                
                # Calculate total value (simplified - just cash for now)
                total_value = cash
                
                # For each holding, we'd need current price (not available in position file)
                # So we'll focus on completed trades (cash changes)
                
                if i > 0:
                    prev_cash = positions[i-1]['positions'].get('CASH', 0)
                    cash_change = cash - prev_cash
                    
                    if abs(cash_change) > 0.01:  # Significant change
                        all_trades.append({
                            'model': model_name,
                            'date': date,
                            'cash_before': prev_cash,
                            'cash_after': cash,
                            'profit': cash_change,
                            'profit_pct': (cash_change / prev_cash * 100) if prev_cash > 0 else 0,
                            'holdings': holdings
                        })
            
            # Calculate model performance
            if positions:
                final_cash = positions[-1]['positions'].get('CASH', 0)
                total_profit = final_cash - initial_cash
                total_profit_pct = (total_profit / initial_cash * 100) if initial_cash > 0 else 0
                
                print(f"   💰 رأس المال الأولي: ${initial_cash:,.2f}")
                print(f"   💵 الرصيد النهائي: ${final_cash:,.2f}")
                print(f"   {'📈' if total_profit > 0 else '📉'} الربح/الخسارة: ${total_profit:,.2f} ({total_profit_pct:+.2f}%)")
                print()
    
    return all_trades

def find_best_trades(trades, limit=10):
    """إيجاد أفضل الصفقات"""
    
    # Sort by profit
    sorted_trades = sorted(trades, key=lambda x: x['profit'], reverse=True)
    
    print("=" * 80)
    print("🏆 أفضل الصفقات (أكبر ربح)")
    print("=" * 80)
    
    for i, trade in enumerate(sorted_trades[:limit], 1):
        print(f"\n{i}. 🎯 الموديل: {trade['model']}")
        print(f"   📅 التاريخ: {trade['date']}")
        print(f"   💰 الرصيد قبل: ${trade['cash_before']:,.2f}")
        print(f"   💵 الرصيد بعد: ${trade['cash_after']:,.2f}")
        print(f"   {'🔥' if trade['profit'] > 0 else '💀'} الربح: ${trade['profit']:,.2f} ({trade['profit_pct']:+.2f}%)")
        if trade['holdings']:
            print(f"   📊 الأسهم: {', '.join([f'{k}: {v}' for k, v in list(trade['holdings'].items())[:3]])}")
    
    return sorted_trades[:limit]

def find_worst_trades(trades, limit=10):
    """إيجاد أسوأ الصفقات"""
    
    # Sort by loss (negative profit)
    sorted_trades = sorted(trades, key=lambda x: x['profit'])
    
    print("\n" + "=" * 80)
    print("💀 أسوأ الصفقات (أكبر خسارة)")
    print("=" * 80)
    
    for i, trade in enumerate(sorted_trades[:limit], 1):
        print(f"\n{i}. ⚠️  الموديل: {trade['model']}")
        print(f"   📅 التاريخ: {trade['date']}")
        print(f"   💰 الرصيد قبل: ${trade['cash_before']:,.2f}")
        print(f"   💵 الرصيد بعد: ${trade['cash_after']:,.2f}")
        print(f"   💀 الخسارة: ${trade['profit']:,.2f} ({trade['profit_pct']:+.2f}%)")
        if trade['holdings']:
            print(f"   📊 الأسهم: {', '.join([f'{k}: {v}' for k, v in list(trade['holdings'].items())[:3]])}")
    
    return sorted_trades[:limit]

def calculate_statistics(trades):
    """حساب الإحصائيات"""
    
    if not trades:
        print("\n❌ مافيش صفقات!")
        return
    
    total_trades = len(trades)
    profitable_trades = [t for t in trades if t['profit'] > 0]
    losing_trades = [t for t in trades if t['profit'] < 0]
    
    total_profit = sum(t['profit'] for t in profitable_trades)
    total_loss = sum(t['profit'] for t in losing_trades)
    net_profit = sum(t['profit'] for t in trades)
    
    win_rate = (len(profitable_trades) / total_trades * 100) if total_trades > 0 else 0
    
    avg_profit = (total_profit / len(profitable_trades)) if profitable_trades else 0
    avg_loss = (total_loss / len(losing_trades)) if losing_trades else 0
    
    print("\n" + "=" * 80)
    print("📊 الإحصائيات العامة")
    print("=" * 80)
    
    print(f"\n📈 عدد الصفقات الكلي: {total_trades}")
    print(f"✅ صفقات رابحة: {len(profitable_trades)} ({win_rate:.1f}%)")
    print(f"❌ صفقات خاسرة: {len(losing_trades)} ({100-win_rate:.1f}%)")
    
    print(f"\n💰 إجمالي الأرباح: ${total_profit:,.2f}")
    print(f"💸 إجمالي الخسائر: ${total_loss:,.2f}")
    print(f"{'📈' if net_profit > 0 else '📉'} صافي الربح: ${net_profit:,.2f}")
    
    print(f"\n📊 متوسط الربح للصفقة: ${avg_profit:,.2f}")
    print(f"📊 متوسط الخسارة للصفقة: ${avg_loss:,.2f}")
    
    if avg_loss != 0:
        profit_factor = abs(total_profit / total_loss)
        print(f"🎯 معامل الربح (Profit Factor): {profit_factor:.2f}")

def main():
    print("=" * 80)
    print("🔍 تحليل الصفقات - FinRL Trading Bot")
    print("=" * 80)
    print()
    
    # Analyze all trades
    all_trades = analyze_all_trades()
    
    if not all_trades:
        print("\n❌ مافيش صفقات للتحليل!")
        return
    
    print(f"\n✅ تم العثور على {len(all_trades)} صفقة")
    
    # Find best trades
    best_trades = find_best_trades(all_trades, limit=10)
    
    # Find worst trades
    worst_trades = find_worst_trades(all_trades, limit=10)
    
    # Statistics
    calculate_statistics(all_trades)
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_trades': len(all_trades),
        'best_trades': best_trades[:5],
        'worst_trades': worst_trades[:5],
        'all_trades': all_trades
    }
    
    with open('/vercel/sandbox/trade_analysis_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "=" * 80)
    print("💾 التقرير محفوظ في: trade_analysis_report.json")
    print("=" * 80)

if __name__ == "__main__":
    main()
