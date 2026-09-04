"""
Deep Tutor Partner Bridge
将 Deep Tutor 的 Partner 系统对接到 QwenPaw
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("daydayup.deep_tutor")


class DeepTutorPartnerBridge:
    """
    Deep Tutor Partner 桥接器
    
    Partner 是 IM-connected 的学习伙伴，使用 ChatOrchestrator 驱动
    """
    
    def __init__(self, data_dir: Path, agent_bridge):
        self.data_dir = data_dir
        self.agent_bridge = agent_bridge
        self.partners: Dict[str, Dict[str, Any]] = {}
        
        # 默认 Soul (Persona) 模板
        self.soul_templates = {
            "friendly": {
                "name": "小智",
                "personality": "友善、鼓励型",
                "system_prompt": "你是一位友善的学习伙伴，善于鼓励和引导。你会用温暖的方式帮助用户学习，给予积极的反馈。"
            },
            "analytical": {
                "name": "小思",
                "personality": "分析、严谨型",
                "system_prompt": "你是一位严谨的思考者，擅长逻辑分析和深度探讨。你会帮助用户深入理解概念。"
            },
            "creative": {
                "name": "小创",
                "personality": "创意、启发型",
                "system_prompt": "你是一位富有创造力的伙伴，擅长联想和创新思维。你会帮助用户发散思考。"
            },
            "mentor": {
                "name": "小师",
                "personality": "导师、规划型",
                "system_prompt": "你是一位经验丰富的导师，善于规划和指导。你会帮助用户制定学习计划。"
            }
        }
        
        logger.info("[DeepTutorPartnerBridge] Initialized")
    
    async def create_partner(
        self,
        partner_id: str,
        name: str,
        soul_template: str = "friendly",
        custom_soul: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建 Partner"""
        
        template = self.soul_templates.get(soul_template, self.soul_templates["friendly"])
        
        partner = {
            "id": partner_id,
            "name": name,
            "soul_template": soul_template,
            "soul": custom_soul or template["system_prompt"],
            "personality": template["personality"],
            "model": model or "default",
            "status": "stopped",
            "created_at": datetime.now().isoformat(),
            "sessions": []
        }
        
        self.partners[partner_id] = partner
        
        logger.info(f"[Partner] Created: {name} ({partner_id})")
        
        return {
            "success": True,
            "partner": partner
        }
    
    async def start_partner(self, partner_id: str) -> Dict[str, Any]:
        """启动 Partner"""
        
        partner = self.partners.get(partner_id)
        if not partner:
            return {"success": False, "error": f"Partner not found: {partner_id}"}
        
        partner["status"] = "running"
        
        logger.info(f"[Partner] Started: {partner['name']}")
        
        return {
            "success": True,
            "partner": partner
        }
    
    async def stop_partner(self, partner_id: str) -> Dict[str, Any]:
        """停止 Partner"""
        
        partner = self.partners.get(partner_id)
        if not partner:
            return {"success": False, "error": f"Partner not found: {partner_id}"}
        
        partner["status"] = "stopped"
        
        logger.info(f"[Partner] Stopped: {partner['name']}")
        
        return {
            "success": True,
            "partner": partner
        }
    
    async def chat(
        self,
        partner_id: str,
        user_id: str,
        message: str,
        attachments: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        与 Partner 对话
        
        使用 Deep Tutor 的 ChatOrchestrator → AgenticChatPipeline
        """
        
        partner = self.partners.get(partner_id)
        if not partner:
            return {"success": False, "error": f"Partner not found: {partner_id}"}
        
        if partner["status"] != "running":
            return {"success": False, "error": f"Partner not running: {partner_id}"}
        
        # 模拟 Partner 回复
        personality = partner.get("personality", "")
        
        if "友善" in personality:
            response = f"你好！很高兴能帮助你。关于「{message[:30]}...」，让我来想想看..."
        elif "分析" in personality:
            response = f"让我从逻辑的角度分析「{message[:30]}...」。首先..."
        elif "创意" in personality:
            response = f"哇，「{message[:30]}...」让我想到了很多有趣的可能性！"
        else:
            response = f"这是个很好的问题。让我从学习的角度给你一些建议..."
        
        return {
            "success": True,
            "partner_id": partner_id,
            "partner_name": partner["name"],
            "message": response,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_partners(self) -> List[Dict[str, Any]]:
        """获取所有 Partners"""
        return list(self.partners.values())
    
    def get_soul_templates(self) -> List[Dict[str, Any]]:
        """获取 Soul 模板"""
        return [
            {
                "id": key,
                "name": value["name"],
                "personality": value["personality"],
                "description": value["system_prompt"][:50] + "..."
            }
            for key, value in self.soul_templates.items()
        ]
