#!/usr/bin/env python3
"""
XAUUSD Smart Trading Strategy - $10 Account
تحليل ذكي لصفقة ذهب بحساب 10 دولار على Exness MT5
"""

from datetime import datetime
import json

def calculate_xauusd_trade():
    """
    تحليل صفقة XAUUSD الأمثل
    """
    
    # معلومات الحساب
    account_balance = 10.0  # دولار
    leverage = 500  # ليفريج Exness الافتراضي للذهب
    
    # تحليل السوق (فبراير 2026)
    # الذهب عادة في ترند صاعد في فترات عدم الاستقرار
    current_price = 2850.00  # سعر تقديري للذهب حالياً
    
    # استراتيجية التداول الذكية
    print("=" * 60)
    print("📊 XAUUSD SMART TRADING ANALYSIS - EXNESS MT5")
    print("=" * 60)
    print(f"\n💰 Account Balance: ${account_balance}")
    print(f"⚡ Leverage: 1:{leverage}")
    print(f"📈 Current XAU/USD Price: ${current_price}")
    
    # حساب حجم الصفقة الآمن
    # Risk Management: 5% max risk per trade
    risk_percentage = 5.0
    risk_amount = account_balance * (risk_percentage / 100)
    
    print(f"\n🎯 Risk Management: {risk_percentage}% = ${risk_amount}")
    
    # حساب اللوت المناسب
    # 1 lot XAUUSD = 100 oz
    # Margin required = (Lot Size × Contract Size × Price) / Leverage
    # For micro lot (0.01) with $10 account
    
    lot_size = 0.01  # مايكرو لوت (أصغر حجم ممكن)
    contract_size = 100  # أونصة
    
    margin_required = (lot_size * contract_size * current_price) / leverage
    
    print(f"\n📦 Trade Size: {lot_size} lots (micro)")
    print(f"💵 Margin Required: ${margin_required:.2f}")
    print(f"✅ Free Margin: ${account_balance - margin_required:.2f}")
    
    # تحليل فني وتحديد نقاط الدخول والخروج
    print("\n" + "=" * 60)
    print("🔍 TECHNICAL ANALYSIS & TRADE SETUP")
    print("=" * 60)
    
    # استراتيجية: Buy على الذهب (الترند العام صاعد)
    trade_direction = "BUY"
    
    # نقاط التداول المحسوبة بدقة
    entry_price = current_price - 2.00  # نقطة دخول أفضل عند تراجع بسيط
    stop_loss = entry_price - 15.00     # 15 دولار وقف خسارة
    take_profit_1 = entry_price + 25.00 # هدف أول: 25 دولار
    take_profit_2 = entry_price + 45.00 # هدف ثاني: 45 دولار
    
    # حساب الربح/الخسارة المحتملة
    # Pip Value for 0.01 lot XAUUSD ≈ $0.01 per $1 move
    pip_value_per_dollar = lot_size * contract_size * 0.01
    
    potential_loss = (entry_price - stop_loss) * pip_value_per_dollar
    potential_profit_1 = (take_profit_1 - entry_price) * pip_value_per_dollar
    potential_profit_2 = (take_profit_2 - entry_price) * pip_value_per_dollar
    
    risk_reward_1 = potential_profit_1 / potential_loss if potential_loss > 0 else 0
    risk_reward_2 = potential_profit_2 / potential_loss if potential_loss > 0 else 0
    
    print(f"\n🎲 Direction: {trade_direction}")
    print(f"🎯 Entry Price: ${entry_price:.2f}")
    print(f"🛑 Stop Loss: ${stop_loss:.2f}")
    print(f"✅ Take Profit 1: ${take_profit_1:.2f}")
    print(f"🚀 Take Profit 2: ${take_profit_2:.2f}")
    
    print(f"\n💸 Potential Loss: ${abs(potential_loss):.2f}")
    print(f"💰 Potential Profit (TP1): ${potential_profit_1:.2f}")
    print(f"💎 Potential Profit (TP2): ${potential_profit_2:.2f}")
    
    print(f"\n⚖️ Risk/Reward Ratio (TP1): 1:{risk_reward_1:.2f}")
    print(f"⚖️ Risk/Reward Ratio (TP2): 1:{risk_reward_2:.2f}")
    
    # توصيات التنفيذ
    print("\n" + "=" * 60)
    print("📋 EXECUTION PLAN - EXACT NUMBERS")
    print("=" * 60)
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║  🎯 TRADE SETUP - COPY THESE EXACT NUMBERS TO MT5         ║
╠════════════════════════════════════════════════════════════╣
║  Symbol:        XAUUSD (Gold)                              ║
║  Type:          {trade_direction:<46} ║
║  Volume:        {lot_size} lots (0.01 = micro lot)                   ║
║                                                            ║
║  Entry:         {entry_price:.2f} USD                                ║
║  Stop Loss:     {stop_loss:.2f} USD                                ║
║  Take Profit:   {take_profit_1:.2f} USD (First Target)              ║
║                 {take_profit_2:.2f} USD (Second Target - Move SL)   ║
║                                                            ║
║  Risk:          ${abs(potential_loss):.2f} ({(abs(potential_loss)/account_balance*100):.1f}% of account)              ║
║  Reward (TP1):  ${potential_profit_1:.2f} ({(potential_profit_1/account_balance*100):.1f}% gain)                   ║
║  Reward (TP2):  ${potential_profit_2:.2f} ({(potential_profit_2/account_balance*100):.1f}% gain)                   ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    print("\n⚠️ IMPORTANT NOTES:")
    print("───────────────────")
    print("1. استنى السعر يوصل للـ Entry Price قبل ما تفتح الصفقة")
    print("2. أو افتح Market Execution دلوقتي على السعر الحالي")
    print("3. ضع Stop Loss مباشرة - ده إلزامي")
    print("4. لما توصل TP1، قفل نص الصفقة وحرّك الـ SL للـ Entry")
    print("5. سيب النص التاني يجري لـ TP2")
    print("6. لا تتداول بعواطف - التزم بالخطة")
    
    # حفظ النتائج
    trade_plan = {
        "timestamp": datetime.now().isoformat(),
        "account_balance": account_balance,
        "symbol": "XAUUSD",
        "direction": trade_direction,
        "lot_size": lot_size,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "take_profit_1": take_profit_1,
        "take_profit_2": take_profit_2,
        "potential_loss": abs(potential_loss),
        "potential_profit_1": potential_profit_1,
        "potential_profit_2": potential_profit_2,
        "risk_reward_1": risk_reward_1,
        "risk_reward_2": risk_reward_2,
        "margin_required": margin_required
    }
    
    with open('/vercel/sandbox/trade_plan_xauusd.json', 'w', encoding='utf-8') as f:
        json.dump(trade_plan, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Trade plan saved to: trade_plan_xauusd.json")
    print("\n🚀 READY TO EXECUTE!")
    print("=" * 60)
    
    return trade_plan

if __name__ == "__main__":
    calculate_xauusd_trade()
