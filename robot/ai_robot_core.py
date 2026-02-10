"""
AI Robot Core - نواة روبوت ذكي قابل للبرمجة
دعم كامل لـ ChatGPT وبرمجة مرئية
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


class AIRobotCore:
    """
    نواة الروبوت الذكي
    - تحكم كامل بالحركة والذكاء الاصطناعي
    - دعم ChatGPT للمحادثة والأوامر الصوتية
    - برمجة مرئية للأطفال والمبتدئين
    """

    def __init__(
        self,
        robot_name: str = "Zaku-AI",
        ai_model: str = "gpt-4",
        log_path: str = "./robot_logs",
        max_steps: int = 100,
        voice_enabled: bool = True
    ):
        self.robot_name = robot_name
        self.ai_model = ai_model
        self.log_path = Path(log_path)
        self.max_steps = max_steps
        self.voice_enabled = voice_enabled

        # حالة الروبوت
        self.position = {"x": 0, "y": 0, "z": 0}
        self.orientation = 0  # درجات
        self.battery_level = 100
        self.sensors = {}
        self.is_active = False

        # ذاكرة المحادثة
        self.conversation_history = []
        self.command_queue = []

        # إنشاء مجلد السجلات
        self.log_path.mkdir(parents=True, exist_ok=True)

        print(f"🤖 {self.robot_name} initialized")
        print(f"🧠 AI Model: {self.ai_model}")
        print(f"🔋 Battery: {self.battery_level}%")

    async def initialize(self):
        """تهيئة الروبوت والاتصال بـ ChatGPT"""
        self.is_active = True
        self.log_action("Robot initialized and ready")
        print(f"✅ {self.robot_name} is now online!")

        # تهيئة الحساسات
        self.sensors = {
            "ultrasonic": {"distance": 0, "unit": "cm"},
            "infrared": {"detected": False},
            "temperature": {"value": 25, "unit": "C"},
            "gyroscope": {"x": 0, "y": 0, "z": 0},
            "camera": {"enabled": True, "resolution": "1080p"}
        }

        return True

    async def chat(self, message: str) -> str:
        """
        محادثة مع الروبوت عبر ChatGPT

        Args:
            message: الرسالة من المستخدم

        Returns:
            رد الروبوت
        """
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        # محاكاة استجابة ChatGPT
        response = await self._process_ai_response(message)

        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        self.log_action(f"Chat - User: {message} | Bot: {response}")
        return response

    async def _process_ai_response(self, message: str) -> str:
        """معالجة الرسالة وإنشاء رد ذكي"""
        message_lower = message.lower()

        # أوامر الحركة
        if "تقدم" in message_lower or "forward" in message_lower:
            await self.move_forward(distance=10)
            return f"حاضر! تحركت للأمام 10 سم 🤖"

        elif "ارجع" in message_lower or "backward" in message_lower:
            await self.move_backward(distance=10)
            return f"راجع للخلف 10 سم ✅"

        elif "يمين" in message_lower or "right" in message_lower:
            await self.turn_right(angle=90)
            return f"استدرت يمين 90 درجة ➡️"

        elif "شمال" in message_lower or "left" in message_lower:
            await self.turn_left(angle=90)
            return f"استدرت شمال 90 درجة ⬅️"

        # معلومات عن الروبوت
        elif "بطارية" in message_lower or "battery" in message_lower:
            return f"🔋 مستوى البطارية: {self.battery_level}%"

        elif "موقع" in message_lower or "position" in message_lower:
            return f"📍 موقعي الحالي: X={self.position['x']}, Y={self.position['y']}, Z={self.position['z']}"

        elif "حساسات" in message_lower or "sensors" in message_lower:
            sensor_info = "\n".join([
                f"  • {name}: {data}"
                for name, data in self.sensors.items()
            ])
            return f"📊 بيانات الحساسات:\n{sensor_info}"

        # تحية
        elif "مرحبا" in message_lower or "hello" in message_lower or "hi" in message_lower:
            return f"مرحباً! أنا {self.robot_name}، الروبوت الذكي. كيف أقدر أساعدك؟ 👋"

        # رد افتراضي
        else:
            return f"فهمت رسالتك: '{message}'. ممكن توضح أكتر أو تعطيني أمر محدد؟ 🤔"

    async def move_forward(self, distance: int = 10):
        """التحرك للأمام"""
        if distance <= 0:
            print("⚠️ المسافة يجب أن تكون أكبر من صفر")
            return False

        # تحديث الموقع بناءً على الاتجاه
        rad = self.orientation * 3.14159 / 180
        import math
        self.position["x"] += int(distance * math.cos(rad))
        self.position["y"] += int(distance * math.sin(rad))

        self.battery_level = max(0, self.battery_level - 1)
        self.log_action(f"Moved forward {distance}cm")

        print(f"➡️ تقدمت {distance} سم")
        await asyncio.sleep(0.5)  # محاكاة الحركة
        return True

    async def move_backward(self, distance: int = 10):
        """التحرك للخلف"""
        if distance <= 0:
            return False

        rad = self.orientation * 3.14159 / 180
        import math
        self.position["x"] -= int(distance * math.cos(rad))
        self.position["y"] -= int(distance * math.sin(rad))

        self.battery_level = max(0, self.battery_level - 1)
        self.log_action(f"Moved backward {distance}cm")

        print(f"⬅️ رجعت للخلف {distance} سم")
        await asyncio.sleep(0.5)
        return True

    async def turn_right(self, angle: int = 90):
        """الدوران لليمين"""
        self.orientation = (self.orientation - angle) % 360
        self.battery_level = max(0, self.battery_level - 0.5)
        self.log_action(f"Turned right {angle} degrees")

        print(f"🔄 استدرت يمين {angle} درجة")
        await asyncio.sleep(0.3)
        return True

    async def turn_left(self, angle: int = 90):
        """الدوران للشمال"""
        self.orientation = (self.orientation + angle) % 360
        self.battery_level = max(0, self.battery_level - 0.5)
        self.log_action(f"Turned left {angle} degrees")

        print(f"🔄 استدرت شمال {angle} درجة")
        await asyncio.sleep(0.3)
        return True

    async def execute_visual_program(self, blocks: List[Dict[str, Any]]):
        """
        تنفيذ برنامج مرئي (Visual Programming)

        Args:
            blocks: قائمة من البلوكات البرمجية

        Example:
            blocks = [
                {"type": "move_forward", "params": {"distance": 20}},
                {"type": "turn_right", "params": {"angle": 90}},
                {"type": "move_forward", "params": {"distance": 15}},
                {"type": "say", "params": {"message": "وصلت للهدف!"}}
            ]
        """
        print(f"🎮 بدأ تنفيذ البرنامج المرئي ({len(blocks)} بلوك)")

        for i, block in enumerate(blocks, 1):
            print(f"\n📦 Block {i}/{len(blocks)}: {block['type']}")

            block_type = block.get("type")
            params = block.get("params", {})

            if block_type == "move_forward":
                await self.move_forward(**params)

            elif block_type == "move_backward":
                await self.move_backward(**params)

            elif block_type == "turn_right":
                await self.turn_right(**params)

            elif block_type == "turn_left":
                await self.turn_left(**params)

            elif block_type == "say":
                message = params.get("message", "")
                print(f"💬 {self.robot_name}: {message}")
                await self.chat(message)

            elif block_type == "wait":
                duration = params.get("duration", 1)
                print(f"⏳ استنى {duration} ثانية...")
                await asyncio.sleep(duration)

            elif block_type == "read_sensor":
                sensor_name = params.get("sensor", "ultrasonic")
                sensor_data = self.sensors.get(sensor_name, {})
                print(f"📊 قراءة حساس {sensor_name}: {sensor_data}")

            else:
                print(f"⚠️ نوع بلوك غير معروف: {block_type}")

        print(f"\n✅ البرنامج المرئي اكتمل بنجاح!")
        self.log_action(f"Visual program completed: {len(blocks)} blocks")

    def log_action(self, action: str):
        """تسجيل الأحداث"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "robot": self.robot_name,
            "action": action,
            "position": self.position.copy(),
            "battery": self.battery_level
        }

        log_file = self.log_path / "robot_actions.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة الروبوت الكاملة"""
        return {
            "name": self.robot_name,
            "active": self.is_active,
            "position": self.position,
            "orientation": self.orientation,
            "battery": self.battery_level,
            "sensors": self.sensors,
            "ai_model": self.ai_model,
            "conversation_count": len(self.conversation_history)
        }

    async def shutdown(self):
        """إيقاف الروبوت"""
        self.is_active = False
        self.log_action("Robot shutdown")
        print(f"🔴 {self.robot_name} offline")


async def demo_run():
    """تجربة سريعة للروبوت"""
    print("="*60)
    print("🚀 DEMO: AI Robot Core - Zaku AI")
    print("="*60)

    # إنشاء روبوت
    robot = AIRobotCore(robot_name="Zaku-Master", ai_model="gpt-4")
    await robot.initialize()

    print("\n--- محادثة مع الروبوت ---")

    # محادثة
    response1 = await robot.chat("مرحبا يا روبوت!")
    print(f"🤖 {response1}")

    response2 = await robot.chat("تقدم للأمام")
    print(f"🤖 {response2}")

    response3 = await robot.chat("كم البطارية؟")
    print(f"🤖 {response3}")

    print("\n--- برنامج مرئي ---")

    # برنامج مرئي: رسم مربع
    square_program = [
        {"type": "say", "params": {"message": "هرسم مربع دلوقتي!"}},
        {"type": "move_forward", "params": {"distance": 20}},
        {"type": "turn_right", "params": {"angle": 90}},
        {"type": "move_forward", "params": {"distance": 20}},
        {"type": "turn_right", "params": {"angle": 90}},
        {"type": "move_forward", "params": {"distance": 20}},
        {"type": "turn_right", "params": {"angle": 90}},
        {"type": "move_forward", "params": {"distance": 20}},
        {"type": "turn_right", "params": {"angle": 90}},
        {"type": "say", "params": {"message": "خلصت المربع! 🎉"}}
    ]

    await robot.execute_visual_program(square_program)

    print("\n--- حالة الروبوت النهائية ---")
    status = robot.get_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))

    await robot.shutdown()


if __name__ == "__main__":
    asyncio.run(demo_run())
