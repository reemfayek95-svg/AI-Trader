# 🚀 تشغيل سريع - Gate.io Trading Bot

## خطوات التشغيل (5 دقائق)

### 1️⃣ احصل على API Keys من Gate.io

1. سجل دخول على [Gate.io](https://www.gate.io)
2. اذهب إلى: **Account** → **API Management** → **Create API Key**
3. فعّل الصلاحيات:
   - ✅ **Read Only** (للاستعلام)
   - ✅ **Spot Trading** (للتداول)
4. احفظ:
   - `API Key`
   - `API Secret` (يظهر مرة واحدة فقط!)

### 2️⃣ احصل على OpenAI API Key

1. اذهب إلى [OpenAI Platform](https://platform.openai.com/api-keys)
2. اضغط **Create new secret key**
3. احفظ المفتاح

### 3️⃣ أضف المفاتيح في .env

```bash
# انسخ ملف المثال
cp .env.example .env

# افتح الملف
nano .env
```

أضف المفاتيح:

```bash
# OpenAI
OPENAI_API_KEY="sk-your-key-here"

# Gate.io
GATE_API_KEY="your-gate-key-here"
GATE_API_SECRET="your-gate-secret-here"
```

احفظ واخرج (Ctrl+X ثم Y ثم Enter)

### 4️⃣ ثبّت المكتبات

```bash
pip install -r requirements.txt
```

### 5️⃣ اختبر الاتصال

```bash
python3 test_gate_connection.py
```

يجب أن ترى:
```
✅ Successfully connected to Gate.io!
💰 Account Balance:
   USDT: 1000.00000000
```

### 6️⃣ شغّل البوت!

```bash
python3 run_gate_trader.py
```

اختر من القائمة:
- **1** = جلسة تداول واحدة
- **2** = تداول مستمر 24/7
- **3** = عرض الأسعار فقط

---

## 🎯 مثال سريع

```bash
# تثبيت
pip install -r requirements.txt

# إعداد .env
cp .env.example .env
# أضف مفاتيحك

# اختبار
python3 test_gate_connection.py

# تشغيل
python3 run_gate_trader.py
# اختر 1 لجلسة واحدة
```

---

## ⚠️ نصائح مهمة

1. **ابدأ برصيد صغير** (100-500 USDT للتجربة)
2. **راقب البوت** في أول 24 ساعة
3. **لا تشارك API Keys** مع أحد
4. **فعّل IP Whitelist** على Gate.io للأمان

---

## 🆘 مشاكل شائعة

### "API credentials not found"
```bash
# تأكد من .env
cat .env | grep GATE_API
```

### "Connection failed"
- تحقق من صحة API Key و Secret
- تأكد من تفعيل Spot Trading
- جرب VPN إذا كان Gate.io محظور

### "OpenAI API error"
```bash
# تأكد من المفتاح
cat .env | grep OPENAI_API_KEY
```

---

## 📞 دعم

- مشاكل؟ افتح [Issue](https://github.com/HKUDS/AI-Trader/issues)
- أسئلة؟ شوف [README_GATE.md](README_GATE.md)

---

**يلا نربح! 🚀💰**
