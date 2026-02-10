"""
Visual Programming UI - واجهة البرمجة المرئية
نظام Drag & Drop لبرمجة الروبوت بدون كود
"""

import json
from typing import List, Dict, Any
from pathlib import Path


class VisualBlock:
    """بلوك برمجي واحد"""

    BLOCK_TYPES = {
        "movement": ["move_forward", "move_backward", "turn_right", "turn_left"],
        "communication": ["say", "listen"],
        "control": ["wait", "repeat", "if_sensor"],
        "sensors": ["read_sensor", "check_distance"]
    }

    def __init__(self, block_type: str, params: Dict[str, Any] = None):
        self.block_type = block_type
        self.params = params or {}
        self.color = self._get_color()
        self.icon = self._get_icon()

    def _get_color(self) -> str:
        """لون البلوك حسب النوع"""
        for category, types in self.BLOCK_TYPES.items():
            if self.block_type in types:
                colors = {
                    "movement": "🟦",
                    "communication": "🟩",
                    "control": "🟨",
                    "sensors": "🟧"
                }
                return colors.get(category, "⬜")
        return "⬜"

    def _get_icon(self) -> str:
        """أيقونة البلوك"""
        icons = {
            "move_forward": "⬆️",
            "move_backward": "⬇️",
            "turn_right": "➡️",
            "turn_left": "⬅️",
            "say": "💬",
            "wait": "⏳",
            "read_sensor": "📊"
        }
        return icons.get(self.block_type, "📦")

    def to_dict(self) -> Dict[str, Any]:
        """تحويل لصيغة قابلة للتنفيذ"""
        return {
            "type": self.block_type,
            "params": self.params
        }

    def __str__(self) -> str:
        params_str = ", ".join([f"{k}={v}" for k, v in self.params.items()])
        return f"{self.color}{self.icon} {self.block_type}({params_str})"


class VisualProgram:
    """برنامج كامل من البلوكات"""

    def __init__(self, name: str = "My Program"):
        self.name = name
        self.blocks: List[VisualBlock] = []

    def add_block(self, block_type: str, **params):
        """إضافة بلوك جديد"""
        block = VisualBlock(block_type, params)
        self.blocks.append(block)
        print(f"✅ Block added: {block}")
        return self

    def remove_block(self, index: int):
        """حذف بلوك"""
        if 0 <= index < len(self.blocks):
            removed = self.blocks.pop(index)
            print(f"🗑️ Block removed: {removed}")
            return True
        return False

    def clear(self):
        """مسح كل البلوكات"""
        self.blocks.clear()
        print("🧹 All blocks cleared")

    def show_program(self):
        """عرض البرنامج"""
        print(f"\n{'='*50}")
        print(f"📋 Program: {self.name}")
        print(f"{'='*50}")

        if not self.blocks:
            print("⚠️ No blocks yet!")
            return

        for i, block in enumerate(self.blocks, 1):
            print(f"{i}. {block}")

        print(f"{'='*50}")
        print(f"Total blocks: {len(self.blocks)}\n")

    def to_executable(self) -> List[Dict[str, Any]]:
        """تحويل لصيغة قابلة للتنفيذ"""
        return [block.to_dict() for block in self.blocks]

    def save(self, filename: str):
        """حفظ البرنامج"""
        data = {
            "name": self.name,
            "blocks": self.to_executable()
        }

        filepath = Path(filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"💾 Program saved to: {filename}")

    @classmethod
    def load(cls, filename: str) -> 'VisualProgram':
        """تحميل برنامج محفوظ"""
        filepath = Path(filename)

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        program = cls(name=data.get("name", "Loaded Program"))

        for block_data in data.get("blocks", []):
            block = VisualBlock(
                block_type=block_data["type"],
                params=block_data.get("params", {})
            )
            program.blocks.append(block)

        print(f"📂 Program loaded from: {filename}")
        return program


class ProgramTemplates:
    """قوالب برامج جاهزة"""

    @staticmethod
    def square(side_length: int = 20) -> VisualProgram:
        """رسم مربع"""
        program = VisualProgram("Draw Square")
        program.add_block("say", message="هرسم مربع!")

        for _ in range(4):
            program.add_block("move_forward", distance=side_length)
            program.add_block("turn_right", angle=90)

        program.add_block("say", message="خلصت المربع!")
        return program

    @staticmethod
    def triangle(side_length: int = 20) -> VisualProgram:
        """رسم مثلث"""
        program = VisualProgram("Draw Triangle")
        program.add_block("say", message="هرسم مثلث!")

        for _ in range(3):
            program.add_block("move_forward", distance=side_length)
            program.add_block("turn_left", angle=120)

        program.add_block("say", message="خلصت المثلث!")
        return program

    @staticmethod
    def circle(segments: int = 12, segment_length: int = 5) -> VisualProgram:
        """رسم دائرة (مُقرّب)"""
        program = VisualProgram("Draw Circle")
        program.add_block("say", message="هرسم دائرة!")

        angle_per_segment = 360 // segments

        for _ in range(segments):
            program.add_block("move_forward", distance=segment_length)
            program.add_block("turn_right", angle=angle_per_segment)

        program.add_block("say", message="خلصت الدائرة!")
        return program

    @staticmethod
    def zigzag(repeats: int = 3, distance: int = 15) -> VisualProgram:
        """حركة زجزاج"""
        program = VisualProgram("Zigzag Pattern")
        program.add_block("say", message="هتحرك زجزاج!")

        for _ in range(repeats):
            program.add_block("move_forward", distance=distance)
            program.add_block("turn_right", angle=45)
            program.add_block("move_forward", distance=distance)
            program.add_block("turn_left", angle=90)

        program.add_block("say", message="خلصت الزجزاج!")
        return program

    @staticmethod
    def patrol(laps: int = 2, side_length: int = 30) -> VisualProgram:
        """دورية مراقبة"""
        program = VisualProgram("Patrol Mode")
        program.add_block("say", message="بدأت الدورية!")

        for lap in range(laps):
            program.add_block("say", message=f"لفة {lap+1}")

            for _ in range(4):
                program.add_block("move_forward", distance=side_length)
                program.add_block("read_sensor", sensor="ultrasonic")
                program.add_block("turn_right", angle=90)
                program.add_block("wait", duration=0.5)

        program.add_block("say", message="انتهت الدورية!")
        return program


def demo_visual_ui():
    """عرض توضيحي للواجهة المرئية"""
    print("="*60)
    print("🎨 Visual Programming UI Demo")
    print("="*60)

    # 1. إنشاء برنامج يدوي
    print("\n--- 1. إنشاء برنامج يدوي ---")
    my_program = VisualProgram("My First Program")
    my_program.add_block("say", message="مرحبا!")
    my_program.add_block("move_forward", distance=30)
    my_program.add_block("turn_right", angle=90)
    my_program.add_block("move_forward", distance=20)
    my_program.add_block("say", message="وصلت!")

    my_program.show_program()

    # 2. استخدام القوالب
    print("\n--- 2. قوالب جاهزة ---")

    print("\n🔷 مربع:")
    square = ProgramTemplates.square(25)
    square.show_program()

    print("\n🔺 مثلث:")
    triangle = ProgramTemplates.triangle(20)
    triangle.show_program()

    print("\n🔵 دائرة:")
    circle = ProgramTemplates.circle(segments=8, segment_length=10)
    circle.show_program()

    print("\n⚡ زجزاج:")
    zigzag = ProgramTemplates.zigzag(repeats=2, distance=15)
    zigzag.show_program()

    print("\n🚔 دورية:")
    patrol = ProgramTemplates.patrol(laps=1, side_length=20)
    patrol.show_program()

    # 3. حفظ وتحميل
    print("\n--- 3. حفظ وتحميل البرامج ---")
    save_path = "/vercel/sandbox/robot/saved_programs"
    Path(save_path).mkdir(parents=True, exist_ok=True)

    my_program.save(f"{save_path}/my_program.json")
    square.save(f"{save_path}/square.json")

    loaded = VisualProgram.load(f"{save_path}/square.json")
    loaded.show_program()

    # 4. تحويل للتنفيذ
    print("\n--- 4. تحويل للتنفيذ ---")
    executable = my_program.to_executable()
    print(json.dumps(executable, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    demo_visual_ui()
