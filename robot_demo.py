#!/usr/bin/env python3
"""
🚀 DEMO SCRIPT - Zaku AI Robot
تشغيل سريع للروبوت الذكي
"""

import asyncio
import sys
from pathlib import Path

# إضافة مجلد robot للمسار
sys.path.insert(0, str(Path(__file__).parent))

from robot.ai_robot_core import AIRobotCore
from robot.visual_programming_ui import ProgramTemplates, VisualProgram
from robot.chatgpt_integration import ChatGPTRobotInterface


async def full_demo():
    """عرض شامل لكل المميزات"""
    print("="*70)
    print("🤖 ZAKU AI ROBOT - Full Demo")
    print("="*70)

    # 1. إنشاء الروبوت
    print("\n[1/5] 🔧 إنشاء الروبوت...")
    robot = AIRobotCore(
        robot_name="Zaku-Master",
        ai_model="gpt-4",
        voice_enabled=True
    )
    await robot.initialize()

    # 2. محادثة ChatGPT
    print("\n[2/5] 🧠 اختبار ChatGPT...")
    chat_interface = ChatGPTRobotInterface(robot_name="Zaku-Master")

    test_messages = [
        "مرحبا!",
        "تقدم 30 سم",
        "لف يمين 90 درجة",
        "كم البطارية؟"
    ]

    for msg in test_messages:
        print(f"\n   👤 User: {msg}")
        response = chat_interface.chat(msg)
        print(f"   🤖 Bot: {response}")

        command = chat_interface.parse_command(msg)
        if command['action'] != 'chat':
            print(f"   ⚙️  Action: {command['action']}")

    # 3. حركات يدوية
    print("\n[3/5] 🎮 اختبار الحركة اليدوية...")
    await robot.move_forward(25)
    await robot.turn_right(90)
    await robot.move_forward(25)
    await robot.turn_right(90)
    await robot.move_forward(25)

    # 4. البرمجة المرئية - رسم مربع
    print("\n[4/5] 🎨 اختبار البرمجة المرئية...")

    print("\n   📦 برنامج 1: مربع")
    square = ProgramTemplates.square(side_length=20)
    square.show_program()
    await robot.execute_visual_program(square.to_executable())

    print("\n   📦 برنامج 2: مثلث")
    triangle = ProgramTemplates.triangle(side_length=15)
    triangle.show_program()
    await robot.execute_visual_program(triangle.to_executable())

    print("\n   📦 برنامج 3: دورية مراقبة")
    patrol = ProgramTemplates.patrol(laps=1, side_length=25)
    patrol.show_program()
    await robot.execute_visual_program(patrol.to_executable())

    # 5. برنامج مخصص
    print("\n[5/5] 🛠️ برنامج مخصص...")
    custom = VisualProgram("Custom Dance")
    custom.add_block("say", message="هبدأ رقصة!")
    custom.add_block("move_forward", distance=15)
    custom.add_block("turn_right", angle=45)
    custom.add_block("move_forward", distance=15)
    custom.add_block("turn_left", angle=90)
    custom.add_block("move_forward", distance=15)
    custom.add_block("say", message="خلصت الرقصة! 🎉")

    custom.show_program()
    await robot.execute_visual_program(custom.to_executable())

    # النتيجة النهائية
    print("\n" + "="*70)
    print("📊 FINAL STATUS")
    print("="*70)

    status = robot.get_status()
    print(f"🤖 Robot: {status['name']}")
    print(f"📍 Position: X={status['position']['x']}, Y={status['position']['y']}, Z={status['position']['z']}")
    print(f"🧭 Orientation: {status['orientation']}°")
    print(f"🔋 Battery: {status['battery']}%")
    print(f"💬 Conversations: {status['conversation_count']}")
    print(f"⚡ Status: {'🟢 Active' if status['active'] else '🔴 Offline'}")

    # حفظ
    custom.save("/vercel/sandbox/robot/saved_programs/demo_custom.json")

    # إغلاق
    await robot.shutdown()

    print("\n" + "="*70)
    print("✅ DEMO COMPLETED SUCCESSFULLY!")
    print("="*70)


async def quick_demo():
    """عرض سريع"""
    print("🚀 Quick Demo - Zaku AI Robot\n")

    robot = AIRobotCore(robot_name="Zaku-Quick")
    await robot.initialize()

    # رسم مربع سريع
    square = ProgramTemplates.square(20)
    await robot.execute_visual_program(square.to_executable())

    print(f"\n✅ Done! Position: {robot.position}, Battery: {robot.battery}%")
    await robot.shutdown()


async def interactive_mode():
    """وضع تفاعلي"""
    print("="*70)
    print("🎮 INTERACTIVE MODE - Zaku AI Robot")
    print("="*70)
    print("\nCommands:")
    print("  - forward/قدام [distance]")
    print("  - backward/ورا [distance]")
    print("  - right/يمين [angle]")
    print("  - left/شمال [angle]")
    print("  - square/مربع [size]")
    print("  - status/حالة")
    print("  - quit/خروج")
    print("="*70 + "\n")

    robot = AIRobotCore(robot_name="Zaku-Interactive")
    await robot.initialize()

    chat = ChatGPTRobotInterface(robot_name="Zaku-Interactive")

    while True:
        try:
            user_input = input("🤖 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'خروج']:
                print("👋 Goodbye!")
                break

            # معالجة الأمر
            response = chat.chat(user_input)
            print(f"🤖 Zaku: {response}")

            command = chat.parse_command(user_input)

            # تنفيذ الأمر
            if command['action'] == 'move_forward':
                await robot.move_forward(**command['params'])
            elif command['action'] == 'move_backward':
                await robot.move_backward(**command['params'])
            elif command['action'] == 'turn_right':
                await robot.turn_right(**command['params'])
            elif command['action'] == 'turn_left':
                await robot.turn_left(**command['params'])
            elif command['action'] == 'program_square':
                square = ProgramTemplates.square(command['params']['side_length'])
                await robot.execute_visual_program(square.to_executable())
            elif command['action'] == 'get_battery':
                print(f"🔋 Battery: {robot.battery_level}%")
            elif command['action'] == 'get_position':
                print(f"📍 Position: {robot.position}")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

    await robot.shutdown()


def main():
    """نقطة الدخول الرئيسية"""
    import sys

    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = "full"

    print("\n🤖 Zaku AI Robot Demo\n")
    print("Available modes:")
    print("  python robot_demo.py full        - Full demo (default)")
    print("  python robot_demo.py quick       - Quick demo")
    print("  python robot_demo.py interactive - Interactive mode")
    print()

    if mode == "quick":
        asyncio.run(quick_demo())
    elif mode == "interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(full_demo())


if __name__ == "__main__":
    main()
