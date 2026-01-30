#!/usr/bin/env python3
"""
احصل على IP الحالي بتاعك عشان تضيفه في Gate.io
"""

import requests
import json


def get_public_ip():
    """Get your public IP address"""
    services = [
        "https://api.ipify.org?format=json",
        "https://api.myip.com",
        "https://ipapi.co/json/",
        "https://ifconfig.me/all.json"
    ]
    
    for service in services:
        try:
            response = requests.get(service, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # Different services return IP in different keys
                ip = data.get('ip') or data.get('ipAddress') or data.get('query')
                
                if ip:
                    return ip
        except:
            continue
    
    return None


def main():
    print("=" * 60)
    print("🌐 الحصول على IP Address بتاعك")
    print("=" * 60)
    
    print("\n🔍 جاري البحث عن IP الحالي...")
    
    ip = get_public_ip()
    
    if ip:
        print(f"\n✅ IP Address بتاعك: {ip}")
        print("\n" + "=" * 60)
        print("📋 خطوات إضافة IP في Gate.io:")
        print("=" * 60)
        print("\n1. روح على Gate.io")
        print("2. Account → API Management")
        print("3. اختار API Key بتاعك")
        print("4. اضغط Edit")
        print("5. في IP Whitelist، اضغط Add")
        print(f"6. اكتب: {ip}")
        print("7. Save")
        print("\n✅ كده البوت هيشتغل من الجهاز ده بس")
        print("⚠️  لو غيرت شبكة/مكان، هتحتاج تضيف IP الجديد")
        
        # Save to file
        with open("my_ip.txt", "w") as f:
            f.write(f"Your IP: {ip}\n")
            f.write(f"Date: {__import__('datetime').datetime.now()}\n")
        
        print(f"\n💾 IP محفوظ في: my_ip.txt")
    else:
        print("\n❌ مش قادر أجيب IP")
        print("جرب يدوي:")
        print("1. روح على: https://whatismyipaddress.com/")
        print("2. انسخ IPv4 Address")
        print("3. ضيفه في Gate.io API settings")


if __name__ == "__main__":
    main()
