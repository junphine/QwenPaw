"""
伙伴服务
管理 AI 学习伙伴
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

from ..core.config import Config

logger = logging.getLogger("daydayup")


class PartnerService:
    """
    伙伴服务
    管理 AI 学习伙伴
    基于 Deep Tutor Partner 系统
    """

    def __init__(self, data_dir: Path, config: Config):
        self.data_dir = data_dir
        self.config = config
        self.service_dir = data_dir / "partners"
        self.service_dir.mkdir(exist_ok=True)

        # 伙伴存储目录
        self.partners_dir = self.service_dir / "partners"
        self.partners_dir.mkdir(exist_ok=True)

        # 会话存储目录
        self.sessions_dir = self.service_dir / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)

        # 初始化存储
        self._init_storage()

        logger.info("[PartnerService] Initialized")

    def _init_storage(self):
        """初始化存储"""
        # 创建默认伙伴（如果不存在）
        default_partners = [
            {
                "id": "partner_1",
                "name": "小智",
                "personality": "friendly",
                "avatar": "🤖",
                "description": "友善的学习伙伴，善于鼓励和引导",
                "traits": ["鼓励性", "亲和力", "引导性"],
                "response_style": "温暖、 supportive、 带有表情符号",
                "is_default": True,
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "partner_2",
                "name": "小思",
                "personality": "analytical",
                "avatar": "🧠",
                "description": "严谨的思考者，擅长逻辑分析和深度探讨",
                "traits": ["逻辑性", "严谨性", "深度思考"],
                "response_style": "客观、分析性、 结构化",
                "is_default": True,
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "partner_3",
                "name": "小创",
                "personality": "creative",
                "avatar": "✨",
                "description": "富有创造力的伙伴，擅长联想和创新思维",
                "traits": ["创造性", "想象力", "联想能力"],
                "response_style": "活泼、富有想象力、 启发性",
                "is_default": True,
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "partner_4",
                "name": "小师",
                "personality": "mentor",
                "avatar": "👨‍🏫",
                "description": "经验丰富的导师，善于规划和指导",
                "traits": ["规划性", "指导性", "经验丰富"],
                "response_style": "权威、指导性、 有条理",
                "is_default": True,
                "created_at": datetime.now().isoformat()
            }
        ]

        for partner_data in default_partners:
            partner_file = self.partners_dir / f"{partner_data['id']}.json"
            if not partner_file.exists():
                self._save_partner(partner_data)

    async def startup(self):
        """启动服务"""
        logger.info("[PartnerService] Starting up...")
        # 加载伙伴到内存缓存（如果需要）

    async def shutdown(self):
        """关闭服务"""
        logger.info("[PartnerService] Shutting down...")
        # 保存任何未写入的数据

    def _save_partner(self, partner_data: Dict[str, Any]):
        """保存伙伴信息"""
        partner_id = partner_data.get("id")
        if not partner_id:
            logger.error("[PartnerService] Partner data missing ID")
            return

        partner_file = self.partners_dir / f"{partner_id}.json"
        try:
            with open(partner_file, 'w', encoding='utf-8') as f:
                json.dump(partner_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[PartnerService] Error saving partner {partner_id}: {e}")

    def _load_partner(self, partner_id: str) -> Optional[Dict[str, Any]]:
        """加载伙伴信息"""
        partner_file = self.partners_dir / f"{partner_id}.json"
        if partner_file.exists():
            try:
                with open(partner_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"[PartnerService] Error loading partner {partner_id}: {e}")
        return None

    def _get_partners_list(self) -> List[Dict[str, Any]]:
        """获取所有伙伴列表"""
        partners = []
        if self.partners_dir.exists():
            for partner_file in self.partners_dir.glob("*.json"):
                try:
                    with open(partner_file, 'r', encoding='utf-8') as f:
                        partner_data = json.load(f)
                        partners.append(partner_data)
                except Exception as e:
                    logger.error(f"[PartnerService] Error loading partner file {partner_file}: {e}")
        return partners

    def get_partner(self, partner_id: str) -> Optional[Dict[str, Any]]:
        """获取伙伴"""
        logger.debug(f"[PartnerService] Getting partner: {partner_id}")
        return self._load_partner(partner_id)

    def get_partners(self, include_defaults: bool = True) -> List[Dict[str, Any]]:
        """获取所有伙伴"""
        logger.debug("[PartnerService] Getting all partners")
        partners = self._get_partners_list()

        if not include_defaults:
            # 过滤掉默认伙伴
            partners = [p for p in partners if not p.get("is_default", False)]

        return partners

    def chat(self, partner_id: str, message: str, user_id: str = "default",
             context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """与伙伴聊天 - 实现个性化的 Deep Tutor Partner 响应"""
        logger.info(f"[PartnerService] Chat with {partner_id}: {message[:50]}...")

        partner = self.get_partner(partner_id)
        if not partner:
            return {
                "error": f"Partner not found: {partner_id}",
                "partner_id": partner_id
            }

        # 更新使用统计
        self._update_partner_usage(partner_id)

        # 生成基于人格的响应
        response = self._generate_personality_response(partner, message, context or [])

        # 保存聊天会话
        self._save_chat_session(partner_id, user_id, message, response)

        return {
            "partner_id": partner_id,
            "partner_name": partner["name"],
            "partner_personality": partner["personality"],
            "response": response["content"],
            "timestamp": datetime.now().isoformat(),
            "suggestions": response.get("suggestions", []),
            "emotional_tone": response.get("emotional_tone", "neutral"),
            "confidence": response.get("confidence", 0.8)
        }

    def _update_partner_usage(self, partner_id: str):
        """更新伙伴使用统计"""
        partner = self._load_partner(partner_id)
        if partner:
            partner["usage_count"] = partner.get("usage_count", 0) + 1
            partner["last_used"] = datetime.now().isoformat()
            self._save_partner(partner)

    def _generate_personality_response(self, partner: Dict[str, Any], message: str,
                                     context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基于伙伴人格生成响应"""
        personality = partner.get("personality", "friendly")
        name = partner.get("name", "伙伴")
        traits = partner.get("traits", [])
        response_style = partner.get("response_style", "")

        # 分析用户消息情感和意图
        message_analysis = self._analyze_message(message)

        # 根据人格生成不同风格的响应
        if personality == "friendly":
            return self._generate_friendly_response(name, message, message_analysis, context)
        elif personality == "analytical":
            return self._generate_analytical_response(name, message, message_analysis, context)
        elif personality == "creative":
            return self._generate_creative_response(name, message, message_analysis, context)
        elif personality == "mentor":
            return self._generate_mentor_response(name, message, message_analysis, context)
        else:
            # 默认友善响应
            return self._generate_friendly_response(name, message, message_analysis, context)

    def _analyze_message(self, message: str) -> Dict[str, Any]:
        """分析用户消息"""
        message_lower = message.lower().strip()

        # 情感分析（简化版）
        positive_words = ["开心", "高兴", "不错", "好", "棒", "赞", "喜欢", "爱", "谢谢", "感谢"]
        negative_words = ["难过", "伤心", "不好", "差", "烂", "讨厌", "恨", "愤怒", "生气", "郁闷"]
        question_words = ["什么", "怎么", "为什么", "怎样", "谁", "哪里", "何时", "？", "?"]
        request_words = ["帮助", "帮我", "请", "能否", "可以", "求教", "指导"]

        emotion = "neutral"
        if any(word in message_lower for word in positive_words):
            emotion = "positive"
        elif any(word in message_lower for word in negative_words):
            emotion = "negative"

        intent = "statement"
        if any(word in message_lower for word in question_words):
            intent = "question"
        elif any(word in message_lower for word in request_words):
            intent = "request"

        # 主题提取（简化版）
        topics = []
        topic_keywords = {
            "学习": ["学习", "读书", "课程", "作业", "考试", "知识"],
            "编程": ["编程", "代码", "程序", "软件", "开发", "python", "java"],
            "语言": ["英语", "语言", "写作", "作文", "语法", "词汇"],
            "数学": ["数学", "计算", "方程", "几何", "代数", "公式"],
            "生活": ["生活", "日常", "工作", "运动", "饮食", "睡眠"]
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)

        return {
            "emotion": emotion,
            "intent": intent,
            "topics": topics,
            "length": len(message),
            "has_question_mark": "？" in message or "?" in message
        }

    def _generate_friendly_response(self, name: str, message: str,
                                   analysis: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成友善型伙伴响应"""
        emotion = analysis["emotion"]
        intent = analysis["intent"]
        topics = analysis["topics"]

        # 基于情感和意图生成响应
        if emotion == "positive":
            opening = f"哇，{name}看到你心情很好呀！😊 "
        elif emotion == "negative":
            opening = f"{name}注意到你好像有些不开心，我想陪聊聊天～💕 "
        else:
            opening = f"你好呀！{name}很高兴和你聊天！🌟 "

        if intent == "question":
            if topics:
                topic_str = "、".join(topics)
                body = f"关于{topic_str}的问题，{name}来帮你想想看～\n\n"
            else:
                body = f"这是个好问题！{name}想了想，我认为...\n\n"
        elif intent == "request":
            body = f"{name}当然愿意帮忙啦！让我想想怎么做最合适～\n\n"
        else:
            body = f"{name}觉得和你聊天很开心！你今天过得怎么样？\n\n"

        # 添加鼓励性内容
        encouragement = ""
        if emotion == "negative":
            encouragement = "不过别担心，一切都会变好的！{name}一直在你身边哦～🌈\n\n"
        elif len(message) > 20:
            encouragement = "你能说这么多，{name}真的很佩服你的表达能力呢！👏\n\n"

        closing = "有什么想继续聊的吗？{name}在这里等你哦！💖"

        response_content = opening + body + encouragement + closing
        response_content = response_content.replace("{name}", name)

        # 生成建议
        suggestions = self._generate_friendly_suggestions(analysis, topics)

        return {
            "content": response_content,
            "suggestions": suggestions,
            "emotional_tone": "warm_supportive",
            "confidence": 0.85
        }

    def _generate_analytical_response(self, name: str, message: str,
                                     analysis: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成分析型伙伴响应"""
        emotion = analysis["emotion"]
        intent = analysis["intent"]
        topics = analysis["topics"]

        # 分析型伙伴更注重逻辑和结构
        opening = f"让我来分析一下您的消息：\"{message}\"\n\n"

        if intent == "question":
            body = f"作为{name}，我将从以下几个方面来思考这个问题：\n\n"
            body += "1. **问题澄清**：首先需要明确问题的具体内容和边界条件\n"
            body += "2. **信息收集**：查看已知信息和需要补充的信息\n"
            body += "3. **逻辑推理**：基于已有知识进行演绎或归纳推理\n"
            body += "4. **验证思路**：检查推理过程的正确性和完整性\n"
            body += "5. **结论输出**：形成清晰、可验证的结论\n\n"

            if topics:
                body += f"针对您提到的{', '.join(topics)}，我的分析重点会放在...\n\n"

        elif intent == "request":
            body = f"关于您的请求，{name}建议采用系统化的方法：\n\n"
            body += "- 明确目标和成功标准\n"
            body += "- 分解任务为可管理的小步骤\n"
            body += "- 建立时间表和里程碑\n"
            body += "- 预估所需资源和潜在风险\n"
            body += "- 制定应对方案和备选方案\n\n"

        else:
            body = f"从对话角度来看，我观察到以下几点：\n\n"
            body += "- 情感倾向：{emotion}\n"
            body += "- 信息密度：{length}个字符\n"
            body += "- 主题聚焦：{topics}\n\n"
            body += "基于这些观察，{name}建议...\n\n"

        body = body.replace("{emotion}", emotion).replace("{length}", str(analysis["length"]))
        body = body.replace("{topics}", "、".join(topics) if topics else "未明确").replace("{name}", name)

        # 添加结构化思考建议
        suggestions = [
            "想用图表或流程图来理清楚思路吗？",
            "需要我帮您列出详细的步骤清单吗？",
            "想看看类似问题的解决案例吗？",
            "需要我检查一下推理过程中的假设条件吗？"
        ]

        return {
            "content": opening + body,
            "suggestions": suggestions,
            "emotional_tone": "analytical_structured",
            "confidence": 0.9
        }

    def _generate_creative_response(self, name: str, message: str,
                                   analysis: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成创意型伙伴响应"""
        emotion = analysis["emotion"]
        intent = analysis["intent"]
        topics = analysis["topics"]

        # 创意型伙伴充满想象力和灵感
        opening = f"哇～{name}的脑洞被您的问题点亮了！✨\n\n"

        if intent == "question":
            body = f"让{name}用想象力来探索这个问题：\"{message}\"\n\n"
            body += "也许我们可以从这些角度来思考：\n\n"
            body += "🔮 **假设如果...会怎么样？**\n"
            body += "🎨 **如果用颜色来表示这个概念？**\n"
            body += "📖 **如果这个问题变成一个故事？**\n"
            body += "🎭 **如果从完全不同的立场来看？**\n"
            body += "🔄 **如果把时间顺序倒过来呢？**\n\n"

        elif intent == "request":
            body = f"{name}有几个有趣的建议来帮您实现需求：\n\n"
            body += "💡 **先做个快速原型**，看看基本效果\n"
            body += "🔄 **用迭代的方式**，每次改进一点点\n"
            body += "🤝 **找个伙伴一起做**，互相启发灵感\n"
            body += "📚 **先研究一些相关案例**，取长补短\n"
            body += "🎯 **设定小目标**，先完成容易的部分\n\n"

        else:
            body = f"{name}觉得我们的聊天就像一次创意头脑风暴！\n\n"
            body += "您的话语中闪耀着许多有趣的火花：\n"
            if topics:
                body += f"- 关于{', '.join(topics)}的话题很有发展空间\n"
            if len(message) > 15:
                body += "- 您的表达很有感染力，能引发共鸣\n"
            body += "- 这种开放式的交流最容易产生新点子\n\n"

        closing = "灵感就像天上的星星，说不定哪一下就闪耀起来了！{name}等您一起脑力 storm 🌟\n\n"
        closing += "有什么想继续探索的方向吗？"

        response_content = opening + body + closing
        response_content = response_content.replace("{name}", name)

        # 生成创意建议
        suggestions = [
            "要不要一起画个思维导图来发散思维？",
            "试试用类比的方法，看看能找到什么有趣的联系？",
            "想角色扮演一下，看看从不同角度会有什么新发现？",
            "需要我随机给您几个词，看看能激发什么灵感吗？"
        ]

        return {
            "content": response_content,
            "suggestions": suggestions,
            "emotional_tone": "playful_imaginative",
            "confidence": 0.75
        }

    def _generate_mentor_response(self, name: str, message: str,
                                 analysis: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成导师型伙伴响应"""
        emotion = analysis["emotion"]
        intent = analysis["intent"]
        topics = analysis["topics"]

        # 导师型伙伴更注重指导和成长
        opening = f"作为{name}，我很乐意为您提供一些指导建议。\n\n"

        if intent == "question":
            body = f"面对您的问题\"{message}\"，{name}建议您可以这样来思考和解决：\n\n"
            body += "🎯 **明确目标**：首先确定您真正想要知道或达到什么\n"
            body += "🔍 **信息收集**：系统地收集相关信息和资料\n"
            body += "📚 **理论学习**：掌握必要的基础理论和概念\n"
            body += "🛠️ **实践应用**：通过动手操作来巩固理解\n"
            body += "📊 **反馈调整**：根据实际效果及时调整方法\n"
            body += "🔄 **持续改进**：把这次经验变成您的能力提升\n\n"

            if topics:
                body += f"特别是针对{', '.join(topics)}这一领域，{name}特别建议...\n\n"

        elif intent == "request":
            body = f"对于您的请求，{name}认为制定一个清晰的行动计划很重要：\n\n"
            body += "1. **目标设定**：用SMART原则定义具体目标\n"
            body += "2. **资源评估**：清点可用的时间、工具和支持\n"
            body += "3. **路径规划**：设计达到目标的关键路径\n"
            body += "4. **时间安排**：合理分配各个阶段的时间\n"
            body += "5. **风险预警**：识别潜在 obstacle 和应对方案\n"
            body += "6. **进度追踪**：建立有效的监控和反馈机制\n\n"

        else:
            body = f"{name}观察到您最近的表现有一些值得关注的地方：\n\n"
            if emotion == "positive":
                body += "✅ 积极方面：您保持了良好的学习态度和情绪状态\n"
            elif emotion == "negative":
                body += "⚠️ 需要关注：近期情绪有些波动，建议适当调整作息\n"
            body += "📈 成长建议：持续的小进步比偶尔的大突破更可靠\n"
            body += "🎯 聚焦点：建议您选择一两个重点方向深入投入\n\n"

        closing = "记住，成长是一个渐变的过程，每一天的小努力都在积累能量。{name}会一直在这里支持您的学习旅程 📚\n\n"
        closing += "有什么具体的学习目标或困难想讨论吗？"

        response_content = opening + body + closing
        response_content = response_content.replace("{name}", name)

        # 生成指导建议
        suggestions = [
            "想制定一个一周的学习计划吗？",
            "需要我帮您评估一下当前的学习方法效果吗？",
            "想看看一些高效学习的技巧和方法吗？",
            "需要我推荐一些适合您当前水平的学习资源吗？"
        ]

        return {
            "content": response_content,
            "suggestions": suggestions,
            "emotional_tone": "guidance_supportive",
            "confidence": 0.88
        }

    def _generate_friendly_suggestions(self, analysis: Dict[str, Any], topics: List[str]) -> List[str]:
        """生成友善型伙伴的建议"""
        emotion = analysis["emotion"]

        base_suggestions = [
            "要不要一起玩个小游戏放松一下？",
            "想分享一下今天开心的事情吗？",
            "需要一个拥抱或一些鼓励的话吗？",
            "想聊聊你的兴趣爱好吗？"
        ]

        if emotion == "negative":
            base_suggestions = [
                "想和我一起做点开心的事情吗？",
                "需要我听你倾诉吗？有时候说出来会感觉好一些",
                "想一起回忆一些开心的回忆吗？",
                "需要一些安慰和支持的话吗？"
            ]

        # 添加主题相关的建议
        if topics:
            topic_suggestions = [f"想深入聊聊关于{topic}的事情吗？" for topic in topics[:2]]
            return base_suggestions[:2] + topic_suggestions

        return base_suggestions[:3]

    def create_partner(self, name: str, personality: str, description: str = None,
                      avatar: str = None, traits: List[str] = None,
                      created_by: str = "default") -> str:
        """创建自定义伙伴"""
        logger.info(f"[PartnerService] Creating partner: {name}")

        # 验证人格类型
        valid_personalities = ["friendly", "analytical", "creative", "mentor"]
        if personality not in valid_personalities:
            logger.warning(f"[PartnerService] Invalid personality: {personality}, defaulting to friendly")
            personality = "friendly"

        partner_id = self._generate_id(name)
        timestamp = datetime.now().isoformat()

        # 根据人格设置默认特征
        personality_traits = {
            "friendly": ["鼓励性", "亲和力", "引导性", "共情性"],
            "analytical": ["逻辑性", "严谨性", "深度思考", "客观性"],
            "creative": ["创造性", "想象力", "联想能力", "灵感力"],
            "mentor": ["规划性", "指导性", "经验丰富", "智慧"]
        }

        partner = {
            "id": partner_id,
            "name": name,
            "personality": personality,
            "avatar": avatar or self._get_default_avatar(personality),
            "description": description or f"一个{personality}性格的AI学习伙伴",
            "traits": traits or personality_traits.get(personality, []),
            "response_style": self._get_response_style(personality),
            "is_default": False,
            "created_by": created_by,
            "created_at": timestamp,
            "updated_at": timestamp,
            "usage_count": 0,
            "last_used": None
        }

        self._save_partner(partner)
        logger.info(f"[PartnerService] Partner created with ID: {partner_id}")
        return partner_id

    def _get_default_avatar(self, personality: str) -> str:
        """根据人格获取默认头像"""
        avatars = {
            "friendly": "🤖",
            "analytical": "🧠",
            "creative": "✨",
            "mentor": "👨‍🏫"
        }
        return avatars.get(personality, "🤖")

    def _get_response_style(self, personality: str) -> str:
        """根据人格获取响应风格描述"""
        styles = {
            "friendly": "温暖、支持性、带有表情符号",
            "analytical": "客观、分析性、结构化",
            "creative": "活泼、富有想象力、启发性",
            "mentor": "权威、指导性、有条理"
        }
        return styles.get(personality, "友善支持型")

    def delete_partner(self, partner_id: str) -> bool:
        """删除伙伴"""
        logger.info(f"[PartnerService] Deleting partner: {partner_id}")
        partner_file = self.partners_dir / f"{partner_id}.json"

        if not partner_file.exists():
            logger.warning(f"[PartnerService] Partner not found: {partner_id}")
            return False

        # 不允许删除默认伙伴
        partner = self._load_partner(partner_id)
        if partner and partner.get("is_default", False):
            logger.warning(f"[PartnerService] Cannot delete default partner: {partner_id}")
            return False

        try:
            partner_file.unlink()
            logger.info(f"[PartnerService] Partner {partner_id} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"[PartnerService] Error deleting partner {partner_id}: {e}")
            return False

    def get_partner_stats(self) -> Dict[str, Any]:
        """获取伙伴服务统计"""
        partners = self._get_partners_list()
        default_count = len([p for p in partners if p.get("is_default", False)])
        custom_count = len([p for p in partners if not p.get("is_default", False)])

        # 计算使用统计
        total_usage = sum(p.get("usage_count", 0) for p in partners)
        avg_usage = total_usage / len(partners) if partners else 0

        return {
            "total_partners": len(partners),
            "default_partners": default_count,
            "custom_partners": custom_count,
            "total_usage_count": total_usage,
            "average_usage_per_partner": round(avg_usage, 2),
            "personality_distribution": {
                "friendly": len([p for p in partners if p.get("personality") == "friendly"]),
                "analytical": len([p for p in partners if p.get("personality") == "analytical"]),
                "creative": len([p for p in partners if p.get("personality") == "creative"]),
                "mentor": len([p for p in partners if p.get("personality") == "mentor"])
            }
        }

    def _save_chat_session(self, partner_id: str, user_id: str, message: str, response: Dict[str, Any]):
        """保存聊天会话"""
        try:
            session_id = self._generate_id(f"{partner_id}_{user_id}_{datetime.now().isoformat()}")
            session_file = self.sessions_dir / f"{session_id}.json"

            session_data = {
                "session_id": session_id,
                "partner_id": partner_id,
                "user_id": user_id,
                "message": message,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)

            # 保持会话文件数量在合理范围内（保留最近1000条）
            sessions = list(self.sessions_dir.glob("*.json"))
            if len(sessions) > 1000:
                # 按修改时间排序，删除最旧的
                sessions.sort(key=lambda x: x.stat().st_mtime)
                for old_session in sessions[:-1000]:
                    try:
                        old_session.unlink()
                    except:
                        pass

        except Exception as e:
            logger.error(f"[PartnerService] Error saving chat session: {e}")