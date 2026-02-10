"""
ChatGPT Integration - دمج كامل مع ChatGPT
للمحادثة الذكية والأوامر الصوتية
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class ChatGPTRobotInterface:
    """
    واجهة تفاعلية مع ChatGPT للروبوت
    - فهم الأوامر باللغة الطبيعية
    - ترجمة الأوامر لحركات
    - محادثة ذكية
    """

    def __init__(
        self,
        robot_name: str = "Zaku-AI",
        openai_api_key: Optional[str] = None,
        model: str = "gpt-4"
    ):
        self.robot_name = robot_name
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = self._build_system_prompt()

        # إضافة System Prompt للتاريخ
        self.conversation_history.append({
            "role": "system",
            "content": self.system_prompt
        })

    def _build_system_prompt(self) -> str:
        """بناء System Prompt للروبوت"""
        return f"""أنت {self.robot_name}، روبوت ذكي قابل للبرمجة.

قدراتك:
- التحرك: للأمام، للخلف، دوران يمين/شمال
- الحساسات: مسافة، حرارة، كاميرا، جيروسكوب
- المحادثة: فهم الأوامر باللغة العربية والإنجليزية
- البرمجة المرئية: تنفيذ سلاسل من الأوامر

قواعد:
1. رد بشكل ودود ومفيد
2. إذا طُلب منك حركة، وضّح الحركة بالضبط
3. إذا كان الأمر غير واضح، اطلب توضيح
4. استخدم أسلوب مصري طبيعي في الردود

أمثلة على الأوامر:
- "اتحرك قدام 20 سم" → move_forward(20)
- "لف يمين 90 درجة" → turn_right(90)
- "ارسم مربع" → square_program()
- "شوف إيه قدامك" → read_sensor(ultrasonic)

الآن أنت جاهز للتفاعل!"""

    def add_user_message(self, message: str):
        """إضافة رسالة المستخدم"""
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

    def add_assistant_message(self, message: str):
        """إضافة رد الروبوت"""
        self.conversation_history.append({
            "role": "assistant",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

    def parse_command(self, user_input: str) -> Dict[str, Any]:
        """
        تحليل الأمر وتحويله لأكشن قابل للتنفيذ

        Returns:
            {
                "action": "move_forward",
                "params": {"distance": 20},
                "confidence": 0.95,
                "response_text": "حاضر، هتحرك قدام 20 سم"
            }
        """
        user_lower = user_input.lower()

        # أوامر الحركة
        if any(word in user_lower for word in ["تقدم", "قدام", "forward", "امشي"]):
            distance = self._extract_number(user_input, default=10)
            return {
                "action": "move_forward",
                "params": {"distance": distance},
                "confidence": 0.9,
                "response_text": f"حاضر، هتحرك قدام {distance} سم 🤖"
            }

        elif any(word in user_lower for word in ["ارجع", "ورا", "backward", "خلف"]):
            distance = self._extract_number(user_input, default=10)
            return {
                "action": "move_backward",
                "params": {"distance": distance},
                "confidence": 0.9,
                "response_text": f"تمام، هرجع {distance} سم للخلف ⬅️"
            }

        elif any(word in user_lower for word in ["يمين", "right", "لف يمين"]):
            angle = self._extract_number(user_input, default=90)
            return {
                "action": "turn_right",
                "params": {"angle": angle},
                "confidence": 0.9,
                "response_text": f"هستدير يمين {angle} درجة ➡️"
            }

        elif any(word in user_lower for word in ["شمال", "left", "لف شمال"]):
            angle = self._extract_number(user_input, default=90)
            return {
                "action": "turn_left",
                "params": {"angle": angle},
                "confidence": 0.9,
                "response_text": f"هستدير شمال {angle} درجة ⬅️"
            }

        # أوامر الرسم
        elif any(word in user_lower for word in ["مربع", "square", "ارسم مربع"]):
            side = self._extract_number(user_input, default=20)
            return {
                "action": "program_square",
                "params": {"side_length": side},
                "confidence": 0.85,
                "response_text": f"تمام، هرسم مربع ضلعه {side} سم! 🔷"
            }

        elif any(word in user_lower for word in ["مثلث", "triangle", "ارسم مثلث"]):
            side = self._extract_number(user_input, default=20)
            return {
                "action": "program_triangle",
                "params": {"side_length": side},
                "confidence": 0.85,
                "response_text": f"حاضر، هرسم مثلث ضلعه {side} سم! 🔺"
            }

        elif any(word in user_lower for word in ["دايرة", "circle", "ارسم دايرة"]):
            return {
                "action": "program_circle",
                "params": {"segments": 12, "segment_length": 5},
                "confidence": 0.85,
                "response_text": "ماشي، هرسم دائرة! 🔵"
            }

        # معلومات
        elif any(word in user_lower for word in ["بطارية", "battery", "طاقة"]):
            return {
                "action": "get_battery",
                "params": {},
                "confidence": 1.0,
                "response_text": "هشوف البطارية دلوقتي 🔋"
            }

        elif any(word in user_lower for word in ["موقع", "position", "فين أنت"]):
            return {
                "action": "get_position",
                "params": {},
                "confidence": 1.0,
                "response_text": "هبعتلك موقعي الحالي 📍"
            }

        elif any(word in user_lower for word in ["حساس", "sensor", "قراءة"]):
            return {
                "action": "read_sensor",
                "params": {"sensor": "ultrasonic"},
                "confidence": 0.8,
                "response_text": "هقرأ الحساسات دلوقتي 📊"
            }

        # محادثة عامة
        else:
            return {
                "action": "chat",
                "params": {"message": user_input},
                "confidence": 0.5,
                "response_text": f"فهمت: '{user_input}'. عايزني أعمل إيه بالضبط؟"
            }

    def _extract_number(self, text: str, default: int = 10) -> int:
        """استخراج رقم من النص"""
        import re
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else default

    def chat(self, message: str) -> str:
        """
        محادثة عادية مع الروبوت
        (بدون استدعاء ChatGPT API الحقيقي - محاكاة)
        """
        self.add_user_message(message)

        # تحليل الأمر
        command_data = self.parse_command(message)
        response = command_data["response_text"]

        self.add_assistant_message(response)
        return response

    def get_conversation_summary(self) -> Dict[str, Any]:
        """ملخص المحادثة"""
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": len([m for m in self.conversation_history if m.get("role") == "user"]),
            "assistant_messages": len([m for m in self.conversation_history if m.get("role") == "assistant"]),
            "history": self.conversation_history
        }

    def save_conversation(self, filepath: str):
        """حفظ المحادثة"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)

        print(f"💾 Conversation saved to: {filepath}")

    def clear_conversation(self):
        """مسح المحادثة (ما عدا System Prompt)"""
        self.conversation_history = [self.conversation_history[0]]
        print("🧹 Conversation cleared")


def demo_chatgpt_integration():
    """عرض توضيحي للدمج مع ChatGPT"""
    print("="*60)
    print("🧠 ChatGPT Integration Demo")
    print("="*60)

    chatbot = ChatGPTRobotInterface(robot_name="Zaku-Pro")

    test_commands = [
        "مرحبا يا روبوت!",
        "اتحرك قدام 30 سم",
        "لف يمين 90 درجة",
        "ارسم مربع ضلعه 25",
        "كم البطارية؟",
        "فين أنت دلوقتي؟",
        "ارسم دائرة",
        "اقرأ الحساسات"
    ]

    for i, cmd in enumerate(test_commands, 1):
        print(f"\n[{i}] 👤 User: {cmd}")

        response = chatbot.chat(cmd)
        print(f"    🤖 Zaku-Pro: {response}")

        command_data = chatbot.parse_command(cmd)
        print(f"    📋 Action: {command_data['action']}")
        print(f"    ⚙️ Params: {command_data['params']}")
        print(f"    ✅ Confidence: {command_data['confidence']*100:.0f}%")

    print("\n" + "="*60)
    summary = chatbot.get_conversation_summary()
    print(f"📊 Conversation Summary:")
    print(f"   Total messages: {summary['total_messages']}")
    print(f"   User messages: {summary['user_messages']}")
    print(f"   Bot messages: {summary['assistant_messages']}")

    # حفظ
    chatbot.save_conversation("/vercel/sandbox/robot/conversations/demo.json")


if __name__ == "__main__":
    demo_chatgpt_integration()
