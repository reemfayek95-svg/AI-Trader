#!/usr/bin/env python3
"""
Gate.io Trading Bot - Quick Start Script
تشغيل سريع لبوت التداول على Gate.io
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent.gate_agent.gate_agent import GateAgent

load_dotenv()


async def main():
    """Main entry point"""
    
    print("=" * 60)
    print("🚀 Gate.io Trading Bot")
    print("=" * 60)
    
    # Check API credentials
    api_key = os.getenv("GATE_API_KEY")
    api_secret = os.getenv("GATE_API_SECRET")
    
    if not api_key or not api_secret:
        print("\n❌ Gate.io API credentials not found!")
        print("\nAdd to .env file:")
        print("GATE_API_KEY=your_api_key_here")
        print("GATE_API_SECRET=your_api_secret_here")
        print("\nGet your API keys from: https://www.gate.io/myaccount/apiv4keys")
        return
    
    # Get OpenAI credentials
    openai_base = os.getenv("OPENAI_API_BASE")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_key:
        print("\n⚠️  OpenAI API key not found!")
        print("Add to .env file:")
        print("OPENAI_API_KEY=your_openai_key_here")
        return
    
    # Initialize agent
    print("\n🔧 Initializing Gate.io Trading Agent...")
    
    agent = GateAgent(
        signature="gate-trader-live",
        basemodel="gpt-4o",  # or "gpt-4", "claude-3.7-sonnet", etc.
        api_key=api_key,
        api_secret=api_secret,
        log_path="./data/gate_agent_data",
        max_steps=30,
        initial_cash=1000.0,
        openai_base_url=openai_base,
        openai_api_key=openai_key
    )
    
    # Initialize
    await agent.initialize()
    
    # Show current portfolio
    print("\n" + "=" * 60)
    print("💼 Current Portfolio")
    print("=" * 60)
    
    portfolio = agent.get_portfolio_summary()
    print(f"\n💰 Balance:")
    for currency, amount in portfolio["balance"].items():
        print(f"   {currency}: {amount:.8f}")
    
    print(f"\n💵 Total Value: ${portfolio['total_value_usdt']:.2f} USDT")
    
    # Ask user what to do
    print("\n" + "=" * 60)
    print("Choose an option:")
    print("=" * 60)
    print("1. Run single trading session")
    print("2. Run continuous trading (every 60 minutes)")
    print("3. Check market prices only")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🚀 Running single trading session...")
        await agent.run_trading_session()
        
        # Show updated portfolio
        portfolio = agent.get_portfolio_summary()
        print(f"\n💵 Updated Total Value: ${portfolio['total_value_usdt']:.2f} USDT")
    
    elif choice == "2":
        interval = input("\nEnter interval in minutes (default: 60): ").strip()
        interval = int(interval) if interval.isdigit() else 60
        
        print(f"\n🔁 Starting continuous trading (every {interval} minutes)...")
        print("Press Ctrl+C to stop\n")
        
        await agent.run_continuous(interval_minutes=interval)
    
    elif choice == "3":
        print("\n📊 Current Market Prices:")
        print("=" * 60)
        
        for pair in agent.trading_pairs:
            ticker = agent.get_ticker(pair)
            if ticker:
                print(f"\n{pair}:")
                print(f"  Last: ${ticker['last']:.2f}")
                print(f"  24h High: ${ticker['high']:.2f}")
                print(f"  24h Low: ${ticker['low']:.2f}")
                print(f"  24h Volume: {ticker['volume']:.2f}")
    
    else:
        print("\n👋 Exiting...")
    
    print("\n" + "=" * 60)
    print("✅ Done!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⛔ Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
