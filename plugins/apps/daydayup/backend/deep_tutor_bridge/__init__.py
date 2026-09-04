"""
Deep Tutor Bridge - 将 Deep Tutor 功能对接到 QwenPaw 本地智能体

这个模块提供 Deep Tutor 核心功能的适配层，使其能在 QwenPaw 环境中运行。
"""

from .agent_bridge import DeepTutorAgentBridge
from .memory_bridge import DeepTutorMemoryBridge
from .partner_bridge import DeepTutorPartnerBridge
from .skill_bridge import DeepTutorSkillBridge

__all__ = [
    "DeepTutorAgentBridge",
    "DeepTutorMemoryBridge",
    "DeepTutorPartnerBridge",
    "DeepTutorSkillBridge",
]
