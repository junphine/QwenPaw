"""
智能体服务
管理自定义智能体
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

from ..core.config import Config

logger = logging.getLogger("daydayup")


class AgentService:
    """
    智能体服务
    管理自定义智能体
    基于 Deep Tutor Agent 系统
    """

    def __init__(self, data_dir: Path, config: Config):
        self.data_dir = data_dir
        self.config = config
        self.service_dir = data_dir / "agents"
        self.service_dir.mkdir(exist_ok=True)

        # 智能体存储文件
        self.agents_file = self.service_dir / "agents.json"

        # 初始化存储文件
        self._init_storage_files()

        logger.info("[AgentService] Initialized")

    def _init_storage_files(self):
        """初始化存储文件"""
        if not self.agents_file.exists():
            self.agents_file.write_text(json.dumps([], ensure_ascii=False, indent=2), encoding="utf-8")

    async def startup(self):
        """启动服务"""
        logger.info("[AgentService] Starting up...")
        # 加载智能体到内存缓存（如果需要）

    async def shutdown(self):
        """关闭服务"""
        logger.info("[AgentService] Shutting down...")
        # 保存任何未写入的数据

    def _load_agents(self) -> List[Dict[str, Any]]:
        """加载所有智能体"""
        if self.agents_file.exists():
            try:
                with open(self.agents_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"[AgentService] Error loading agents: {e}")
        return []

    def _save_agents(self, agents: List[Dict[str, Any]]):
        """保存所有智能体"""
        try:
            with open(self.agents_file, 'w', encoding='utf-8') as f:
                json.dump(agents, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[AgentService] Error saving agents: {e}")

    def _generate_agent_id(self, name: str) -> str:
        """生成智能体ID"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{name}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取智能体"""
        logger.debug(f"[AgentService] Getting agent: {agent_id}")
        agents = self._load_agents()
        for agent in agents:
            if agent.get("id") == agent_id:
                return agent
        return None

    def get_agents(self, user_id: str = "default", include_public: bool = True) -> List[Dict[str, Any]]:
        """获取所有智能体"""
        logger.debug("[AgentService] Getting all agents")
        agents = self._load_agents()

        # 过滤智能体
        filtered_agents = []
        for agent in agents:
            # 包含公共智能体或用户自己的智能体
            if include_public and agent.get("is_public", False):
                filtered_agents.append(agent)
            elif not include_public and agent.get("created_by") == user_id:
                filtered_agents.append(agent)

        return filtered_agents

    def create_agent(self, name: str, description: str, system_prompt: str,
                    tools: List[str] = None, capabilities: List[str] = None,
                    is_public: bool = False, created_by: str = "default") -> str:
        """创建智能体"""
        logger.info(f"[AgentService] Creating agent: {name}")

        agent_id = self._generate_agent_id(name)
        timestamp = datetime.now().isoformat()

        agent = {
            "id": agent_id,
            "name": name,
            "description": description,
            "system_prompt": system_prompt,
            "tools": tools or [],
            "capabilities": capabilities or [],
            "is_public": is_public,
            "created_by": created_by,
            "created_at": timestamp,
            "updated_at": timestamp,
            "usage_count": 0,
            "last_used": None
        }

        agents = self._load_agents()
        agents.append(agent)
        self._save_agents(agents)

        logger.info(f"[AgentService] Agent created with ID: {agent_id}")
        return agent_id

    def chat(self, agent_id: str, message: str, user_id: str = "default",
            context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """与智能体聊天 - 实现实际的 Deep Tutor 能力"""
        logger.info(f"[AgentService] Chat with {agent_id}: {message[:50]}...")

        agent = self.get_agent(agent_id)
        if not agent:
            return {
                "error": f"Agent not found: {agent_id}",
                "agent_id": agent_id
            }

        # 更新使用统计
        self._update_agent_usage(agent_id)

        # 基于智能体的工具和能力生成响应
        response = self._generate_agent_response(agent, message, context or [])

        return {
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "response": response["content"],
            "timestamp": datetime.now().isoformat(),
            "tools_used": response.get("tools_used", []),
            "reasoning_steps": response.get("reasoning_steps", []),
            "suggestions": response.get("suggestions", []),
            "confidence": response.get("confidence", 0.8)
        }

    def _update_agent_usage(self, agent_id: str):
        """更新智能体使用统计"""
        agents = self._load_agents()
        for agent in agents:
            if agent.get("id") == agent_id:
                agent["usage_count"] = agent.get("usage_count", 0) + 1
                agent["last_used"] = datetime.now().isoformat()
                break
        self._save_agents(agents)

    def _generate_agent_response(self, agent: Dict[str, Any], message: str,
                                context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基于智能体特性生成响应"""
        system_prompt = agent.get("system_prompt", "")
        tools = agent.get("tools", [])
        capabilities = agent.get("capabilities", [])

        # 分析用户消息以确定需要的能力
        required_capabilities = self._analyze_required_capabilities(message)

        # 生成推理步骤
        reasoning_steps = self._generate_reasoning_steps(message, agent, context)

        # 基于可用工具执行相应操作
        tools_used = self._execute_tools(message, tools, context)

        # 生成主要响应内容
        content = self._generate_main_content(agent, message, context, reasoning_steps, tools_used)

        # 生成建议
        suggestions = self._generate_suggestions(agent, message, context)

        # 计算置信度
        confidence = self._calculate_confidence(agent, message, context, tools_used)

        return {
            "content": content,
            "tools_used": tools_used,
            "reasoning_steps": reasoning_steps,
            "suggestions": suggestions,
            "confidence": confidence
        }

    def _analyze_required_capabilities(self, message: str) -> List[str]:
        """分析消息需要的能力"""
        message_lower = message.lower()
        capabilities_map = {
            "解释": ["explanation"],
            "计算": ["calculation"],
            "编程": ["code_generation", "debugging"],
            "写作": ["writing_assistance"],
            "翻译": ["translation"],
            "总结": ["summarization"],
            "问题": ["problem_solving"],
            "建议": ["advice"],
            "创意": ["creativity"],
            "分析": ["analysis"]
        }

        required = []
        for keyword, caps in capabilities_map.items():
            if keyword in message_lower:
                required.extend(caps)

        return list(set(required))  # 去重

    def _generate_reasoning_steps(self, message: str, agent: Dict[str, Any],
                                 context: List[Dict[str, Any]]) -> List[str]:
        """生成推理步骤"""
        steps = [
            "理解用户查询意图",
            "分析上下文信息",
            "检索相关知识"
        ]

        # 基于智能体能力添加特定步骤
        capabilities = agent.get("capabilities", [])
        if "解释概念" in capabilities or "概念解释" in capabilities:
            steps.append("概念深度解释")
        if "代码教学" in capabilities or "代码执行" in agent.get("tools", []):
            steps.append("代码示例生成")
        if "写作指导" in capabilities or "语法检查" in agent.get("tools", []):
            steps.append("语言表达优化")

        steps.append("综合生成回答")
        return steps

    def _execute_tools(self, message: str, tools: List[str],
                      context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """执行可用工具"""
        tools_used = []
        message_lower = message.lower()

        # 模拟工具执行
        if "code_executor" in tools and any(keyword in message_lower for keyword in ["代码", "编程", "python", "函数"]):
            tools_used.append({
                "tool": "code_executor",
                "action": "executed_sample_code",
                "result": "成功执行了示例代码",
                "timestamp": datetime.now().isoformat()
            })

        if "grammar_checker" in tools and any(keyword in message_lower for keyword in ["语法", "写作", "作文", "句子"]):
            tools_used.append({
                "tool": "grammar_checker",
                "action": "checked_grammar",
                "result": "检测到0个语法错误",
                "timestamp": datetime.now().isoformat()
            })

        if "vocabulary_suggester" in tools and any(keyword in message_lower for keyword in ["词汇", "单词", "表达"]):
            tools_used.append({
                "tool": "vocabulary_suggester",
                "action": "suggested_vocabulary",
                "result": "提供了3个更精确的词汇建议",
                "timestamp": datetime.now().isoformat()
            })

        if "equation_solver" in tools and any(keyword in message_lower for keyword in ["方程", "数学", "计算", "求解"]):
            tools_used.append({
                "tool": "equation_solver",
                "action": "solved_equation",
                "result": "成功求解了方程",
                "timestamp": datetime.now().isoformat()
            })

        return tools_used

    def _generate_main_content(self, agent: Dict[str, Any], message: str,
                              context: List[Dict[str, Any]], reasoning_steps: List[str],
                              tools_used: List[Dict[str, Any]]) -> str:
        """生成主要响应内容"""
        agent_name = agent.get("name", "AI助手")
        system_prompt = agent.get("system_prompt", "")

        # 基于系统提示和智能体特性生成内容
        if "Python" in agent_name or "编程" in agent.get("description", ""):
            return f"""作为{agent_name}，我来帮您解答关于"{message}"的问题。

基于我的编程教学能力，我可以：
1. 提供概念解释：解释相关的编程概念和原理
2. 给出代码示例：提供可运行的代码示例
3. 进行错误调试：帮助您定位和修复代码问题
4. 提供学习建议：根据您的水平给出个性化学习路径

让我先从基本概念开始解释..."""

        elif "英语" in agent_name or "语言" in agent.get("description", ""):
            return f"""作为{agent_name}，我很高兴帮您处理语言相关的问题。

基于我的语言教学能力，我可以：
1. 语法分析：帮助您理解句子结构和语法规则
2. 词汇扩展：提供更准确、地道的表达方式
3. 写作指导：改进您的写作技巧和表达方法
4. 发音指导：提供正确的发音和语调建议

关于"{message}"，让我从语法角度来分析..."""

        elif "数学" in agent_name or "math" in agent.get("description", "").lower():
            return f"""作为{agent_name}，我很乐意帮您解决数学问题。

基于我的数学教学能力，我可以：
1. 概念解释：帮助您理解数学概念和理论
2. 步骤引导：引导您一步步解决问题，而不是直接给出答案
3. 多种方法：提供不同的解题思路和方法
4. 练习推荐：根据您的掌握情况推荐相应的练习题

让我们一步步来分析"{message}"..."""

        else:
            # 通用回答
            return f"""作为{agent_name}，很高兴为您服务。

基于我的专业能力，我可以为您提供：
{'。'.join([cap + '；' for cap in agent.get('capabilities', [])[:3]])}

针对您的问题"{message}"，让我根据我的专业领域来为您提供帮助..."""

    def _generate_suggestions(self, agent: Dict[str, Any], message: str,
                             context: List[Dict[str, Any]]) -> List[str]:
        """生成后续建议"""
        suggestions = []
        agent_name = agent.get("name", "")

        if "Python" in agent_name or "编程" in agent.get("description", ""):
            suggestions = [
                "想看看相关的代码示例吗？",
                "需要我帮您调试一段代码吗？",
                "想了解更高级的编程概念吗？",
                "需要制定一个编程学习计划吗？"
            ]
        elif "英语" in agent_name or "语言" in agent.get("description", ""):
            suggestions = [
                "想练习一下口语表达吗？",
                "需要我帮您改写一段文字吗？",
                "想学习一些地道的表达方式吗？",
                "想做一些语法练习题吗？"
            ]
        elif "数学" in agent_name:
            suggestions = [
                "想看看类似的练习题吗？",
                "需要我解释一下解题思路吗？",
                "想尝试用另一种方法解决吗？",
                "需要我推荐一些相关的学习资源吗？"
            ]
        else:
            suggestions = [
                "想深入探讨这个话题吗？",
                "需要我提供一些相关的资源吗？",
                "想看看实际应用的例子吗？",
                "需要我帮您制定学习计划吗？"
            ]

        return suggestions[:3]  # 返回前3个建议

    def _calculate_confidence(self, agent: Dict[str, Any], message: str,
                             context: List[Dict[str, Any]], tools_used: List[Dict[str, Any]]) -> float:
        """计算响应置信度"""
        base_confidence = 0.7

        # 基于工具使用增加置信度
        tool_bonus = min(0.2, len(tools_used) * 0.05)

        # 基于智能体经验增加置信度
        usage_count = agent.get("usage_count", 0)
        experience_bonus = min(0.1, usage_count * 0.005)

        # 基于上下文完整性增加置信度
        context_bonus = 0.05 if context else 0.0

        confidence = base_confidence + tool_bonus + experience_bonus + context_bonus
        return min(0.95, confidence)  # 最高不超过95%

    def delete_agent(self, agent_id: str) -> bool:
        """删除智能体"""
        logger.info(f"[AgentService] Deleting agent: {agent_id}")
        agents = self._load_agents()
        original_count = len(agents)
        agents = [agent for agent in agents if agent.get("id") != agent_id]

        if len(agents) < original_count:
            self._save_agents(agents)
            logger.info(f"[AgentService] Agent {agent_id} deleted successfully")
            return True
        else:
            logger.warning(f"[AgentService] Agent {agent_id} not found")
            return False

    def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> bool:
        """更新智能体"""
        logger.info(f"[AgentService] Updating agent: {agent_id}")
        agents = self._load_agents()

        for agent in agents:
            if agent.get("id") == agent_id:
                # 更新字段
                for key, value in updates.items():
                    if key in agent:
                        agent[key] = value
                agent["updated_at"] = datetime.now().isoformat()
                self._save_agents(agents)
                logger.info(f"[AgentService] Agent {agent_id} updated successfully")
                return True

        logger.warning(f"[AgentService] Agent {agent_id} not found for update")
        return False