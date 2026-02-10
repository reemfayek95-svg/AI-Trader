"""
🤖 AI Robot Package - Zaku AI
أقوى روبوت ذكي قابل للبرمجة
"""

from .ai_robot_core import AIRobotCore
from .visual_programming_ui import VisualProgram, VisualBlock, ProgramTemplates
from .chatgpt_integration import ChatGPTRobotInterface

__version__ = "1.0.0"
__author__ = "AI Trader Team"

__all__ = [
    "AIRobotCore",
    "VisualProgram",
    "VisualBlock",
    "ProgramTemplates",
    "ChatGPTRobotInterface"
]
