"""
趣学习 (Daydayup) - AI 学习伴侣 v2.0
基于 Deep Tutor 架构，适配 QwenPaw 环境

完整的八大核心功能：
1. Home - 主页学习空间
2. Partners - AI 学习伙伴
3. My Agents - 我的智能体
4. Co-Writer - 协同写作
5. Book - 交互式书本
6. Learning Space - 学习空间
7. Memory - 三层记忆系统
8. Knowledge Center - 知识中心

作者：0+1+2≠3 Team 115886
版本：2.3.0
"""

__version__ = "2.3.0"

import logging
import sys
import os
from pathlib import Path
from typing import Optional

plugin_dir = Path(__file__).parent
# 添加插件目录和deep-tutor-api-client到 Python 路径
deep_tutor_api_dir = plugin_dir / 'deep-tutor-api-client'
if str(plugin_dir) not in sys.path:
    sys.path.insert(0, str(plugin_dir))
    sys.path.insert(0, str(deep_tutor_api_dir))

# 导入核心插件
from backend.core.plugin import DaydayupPlugin
from backend.tools.plugin import DaydayupMemoryToolPlugin


# Module-level plugin instance (required for QwenPaw 2.0)
tools_plugin = DaydayupMemoryToolPlugin()

# 创建插件实例
plugin = DaydayupPlugin([tools_plugin])


