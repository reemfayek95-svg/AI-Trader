# 🤖 AI Robot - Zaku AI

**أقوى روبوت ذكي قابل للبرمجة مع ChatGPT وبرمجة مرئية**

---

## 🌟 المميزات

### ✅ ذكاء اصطناعي متقدم
- 🧠 **دمج ChatGPT**: محادثة ذكية بالعربي والإنجليزي
- 🎯 **فهم الأوامر الطبيعية**: "اتحرك قدام 20 سم" → ينفذها تلقائي
- 🗣️ **أوامر صوتية** (قريباً)

### 🎮 برمجة مرئية بدون كود
- 🧩 **Drag & Drop**: رص البلوكات وشغّل
- 📦 **قوالب جاهزة**: مربع، مثلث، دائرة، دورية
- 💾 **حفظ البرامج**: خزّن برامجك وشغّلها لاحقاً

### 🚀 حركة وتحكم كامل
- ⬆️ تقدم / ⬇️ رجوع
- ➡️ دوران يمين / ⬅️ دوران شمال
- 📊 قراءة حساسات (مسافة، حرارة، كاميرا)
- 🔋 مراقبة البطارية

### 🛠️ قابل للتوسع
- 🔌 أضف حساسات جديدة
- 🎨 صمم برامجك الخاصة
- 🌐 ربط مع API خارجي

---

## 🚀 Quick Start

### 1. تشغيل سريع - Demo

```bash
# نواة الروبوت
python robot/ai_robot_core.py

# البرمجة المرئية
python robot/visual_programming_ui.py

# دمج ChatGPT
python robot/chatgpt_integration.py
```

### 2. استخدام في كودك

```python
import asyncio
from robot.ai_robot_core import AIRobotCore
from robot.visual_programming_ui import ProgramTemplates

async def my_robot():
    # إنشاء روبوت
    robot = AIRobotCore(robot_name="My-Zaku", ai_model="gpt-4")
    await robot.initialize()

    # محادثة
    response = await robot.chat("ارسم مربع")
    print(response)

    # برنامج مرئي
    program = ProgramTemplates.square(side_length=30)
    await robot.execute_visual_program(program.to_executable())

    # إغلاق
    await robot.shutdown()

asyncio.run(my_robot())
```

---

## 📦 الملفات الأساسية

| الملف | الوصف |
|------|-------|
| `ai_robot_core.py` | 🤖 نواة الروبوت - حركة، حساسات، ذكاء |
| `visual_programming_ui.py` | 🎨 البرمجة المرئية - بلوكات، قوالب |
| `chatgpt_integration.py` | 🧠 دمج ChatGPT - محادثة، أوامر طبيعية |
| `README.md` | 📖 التوثيق (أنت هنا!) |

---

## 🎮 أمثلة البرمجة المرئية

### مربع 🔷
```python
from robot.visual_programming_ui import ProgramTemplates

square = ProgramTemplates.square(side_length=25)
square.show_program()
# Output:
# 1. 🟩💬 say(message=هرسم مربع!)
# 2. 🟦⬆️ move_forward(distance=25)
# 3. 🟦➡️ turn_right(angle=90)
# ...
```

### مثلث 🔺
```python
triangle = ProgramTemplates.triangle(side_length=20)
await robot.execute_visual_program(triangle.to_executable())
```

### دائرة 🔵
```python
circle = ProgramTemplates.circle(segments=12, segment_length=5)
```

### دورية مراقبة 🚔
```python
patrol = ProgramTemplates.patrol(laps=2, side_length=30)
```

---

## 🧠 أمثلة ChatGPT

```python
from robot.chatgpt_integration import ChatGPTRobotInterface

chatbot = ChatGPTRobotInterface(robot_name="Zaku-Master")

# محادثة
chatbot.chat("مرحبا!")
# → "مرحباً! أنا Zaku-Master، الروبوت الذكي. كيف أقدر أساعدك؟"

chatbot.chat("اتحرك قدام 50 سم")
# → "حاضر، هتحرك قدام 50 سم 🤖"
# Action: move_forward(distance=50)

chatbot.chat("ارسم مربع ضلعه 30")
# → "تمام، هرسم مربع ضلعه 30 سم! 🔷"
# Action: program_square(side_length=30)

chatbot.chat("كم البطارية؟")
# → "🔋 مستوى البطارية: 95%"
```

---

## 🛠️ التخصيص

### إضافة حركة جديدة
```python
class AIRobotCore:
    async def jump(self, height: int = 10):
        """القفز"""
        self.position["z"] += height
        self.log_action(f"Jumped {height}cm")
        print(f"🦘 قفزت {height} سم!")
```

### إضافة بلوك جديد
```python
class VisualBlock:
    BLOCK_TYPES = {
        "movement": ["move_forward", "jump"],  # أضف "jump"
        # ...
    }
```

### ربط بـ Hardware حقيقي
```python
import RPi.GPIO as GPIO  # Raspberry Pi

class HardwareRobot(AIRobotCore):
    async def move_forward(self, distance: int):
        # تحكم في موتورات حقيقية
        GPIO.output(MOTOR_PIN, GPIO.HIGH)
        await asyncio.sleep(distance / 10)
        GPIO.output(MOTOR_PIN, GPIO.LOW)
```

---

## 📊 Architecture

```
robot/
├── ai_robot_core.py           # 🤖 النواة الذكية
├── visual_programming_ui.py   # 🎨 البرمجة المرئية
├── chatgpt_integration.py     # 🧠 ChatGPT
├── robot_logs/                # 📝 السجلات
├── saved_programs/            # 💾 البرامج المحفوظة
└── conversations/             # 💬 المحادثات
```

---

## 🔋 الحالة والبيانات

### حالة الروبوت
```python
status = robot.get_status()
# {
#   "name": "Zaku-AI",
#   "active": true,
#   "position": {"x": 20, "y": 10, "z": 0},
#   "orientation": 90,
#   "battery": 87,
#   "sensors": {...},
#   "conversation_count": 12
# }
```

### السجلات
```json
// robot_logs/robot_actions.jsonl
{
  "timestamp": "2026-02-10T15:30:00",
  "robot": "Zaku-AI",
  "action": "Moved forward 20cm",
  "position": {"x": 20, "y": 0, "z": 0},
  "battery": 99
}
```

---

## 🎯 Use Cases

### 1. التعليم 🎓
- تعليم البرمجة للأطفال
- ورش عمل الروبوتات
- مسابقات البرمجة

### 2. Automation 🏭
- دوريات مراقبة
- نقل مواد
- فحص بيئي

### 3. البحث 🔬
- تجارب AI
- تطوير خوارزميات
- Simulation

### 4. الترفيه 🎮
- ألعاب تفاعلية
- عروض روبوتية
- مسابقات

---

## 🚀 Roadmap

- [x] ✅ نواة الروبوت
- [x] ✅ البرمجة المرئية
- [x] ✅ دمج ChatGPT
- [ ] 🔄 أوامر صوتية (Voice Commands)
- [ ] 🔄 تطبيق ويب تفاعلي
- [ ] 🔄 دعم Raspberry Pi
- [ ] 🔄 Computer Vision (كاميرا ذكية)
- [ ] 🔄 Multi-Robot Coordination

---

## 🤝 المساهمة

عايز تساهم؟ Perfect!

1. Fork المشروع
2. أنشئ branch جديد
3. اعمل التعديلات
4. ابعت Pull Request

---

## 📄 License

MIT License - استخدمه زي ما تحب!

---

## 🙏 شكر خاص

- 🧠 **OpenAI** - ChatGPT API
- 🤖 **AI Trader Project** - البنية الأساسية
- 🎨 **Community** - الأفكار والدعم

---

<div align="center">

**🌟 إذا عجبك المشروع، اديله Star! ⭐**

**🤖 صنع بحب في مصر 🇪🇬**

**Built with ❤️ for the future of AI Robotics**

</div>

---

## 📞 الدعم

- 🐛 **Issues**: [GitHub Issues](https://github.com/YOUR_REPO/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/YOUR_REPO/discussions)
- 📧 **Email**: support@zakuai.com

---

<div align="center">
  <img src="../assets/AI-Trader-log.png" width="100" />
  <p><em>Powered by AI Trader Platform</em></p>
</div>
