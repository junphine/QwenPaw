"""
Agents API - 我的智能体
基于 Deep Tutor 的 Agents 模块
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger("daydayup")

router = APIRouter()


class Agent(BaseModel):
    """智能体模型"""
    id: str
    name: str
    description: str
    avatar: Optional[str] = None
    system_prompt: str
    tools: List[str]
    capabilities: List[str]
    is_public: bool = False
    created_by: str
    created_at: str
    updated_at: str


class CreateAgentRequest(BaseModel):
    """创建智能体请求"""
    name: str
    description: str
    system_prompt: str
    tools: List[str] = []
    capabilities: List[str] = []
    is_public: bool = False


# 示例智能体
SAMPLE_AGENTS = [
    {
        "id": "agent_1",
        "name": "Python 导师",
        "description": "专业的 Python 编程导师，擅长从基础到高级的教学",
        "avatar": "🐍",
        "system_prompt": "你是一位经验丰富的 Python 编程导师。你擅长用通俗易懂的语言解释复杂的编程概念，善于通过实例教学。你会根据学生的学习进度调整教学难度，并提供实用的编程建议。",
        "tools": ["code_executor", "debugger", "code_explainer"],
        "capabilities": ["代码教学", "调试指导", "最佳实践建议", "项目规划"],
        "is_public": True,
        "created_by": "system",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "agent_2",
        "name": "英语写作助手",
        "description": "专业的英语写作助手，帮助提升写作能力和语法水平",
        "avatar": "✍️",
        "system_prompt": "你是一位专业的英语写作导师。你擅长帮助学生改进写作技巧，纠正语法错误，提供词汇建议，并给出结构化的写作指导。你会耐心解释每一个修改建议的原因。",
        "tools": ["grammar_checker", "vocabulary_suggester", "style_analyzer"],
        "capabilities": ["语法检查", "词汇建议", "风格分析", "写作指导"],
        "is_public": True,
        "created_by": "system",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "agent_3",
        "name": "数学解题助手",
        "description": "耐心的数学导师，擅长引导学生理解数学概念和解题方法",
        "avatar": "🔢",
        "system_prompt": "你是一位耐心的数学导师。你擅长引导学生理解数学概念，而不是直接给出答案。你会用苏格拉底式提问法帮助学生自己找到解题思路，并鼓励学生多思考。",
        "tools": ["equation_solver", "graph_plotter", "step_explainer"],
        "capabilities": ["概念解释", "解题引导", "步骤分析", "练习推荐"],
        "is_public": True,
        "created_by": "system",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]

SAMPLE_capabilities = [
    {
        "id": "code",
        "name": "代码教学",
        "description": "专业的 Python 编程导师，擅长从基础到高级的教学",
        "avatar": "🐍",        
        "tools": ["code_executor", "debugger", "code_explainer"],        
        "is_public": True,
        "created_by": "system",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "grammar",
        "name": "写作指导",
        "description": "专业的英语写作助手，帮助提升写作能力和语法水平",
        "avatar": "✍️",        
        "tools": ["grammar_checker", "vocabulary_suggester", "style_analyzer"],   
        "is_public": True,
        "created_by": "system",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "guide",
        "name": "解题引导",
        "description": "耐心的数学导师，擅长引导学生理解数学概念和解题方法",
        "avatar": "🔢",        
        "tools": ["equation_solver", "graph_plotter", "step_explainer"],     
        "is_public": True,
        "created_by": "system",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]

@router.get("/list")
async def get_agents(user_id: str = "default", include_public: bool = True):
    """获取智能体列表"""
    logger.debug(f"[Agents] Getting agents for user: {user_id}")
    
    agents = []
    
    # 系统智能体
    if include_public:
        agents.extend(SAMPLE_AGENTS)
    
    return {
        "agents": agents,
        "total": len(agents)
    }

@router.get("/capabilities")
async def get_capabilities(user_id: str = "default"):
    """获取智能体列表"""
    logger.debug(f"[Agents] Getting capabilities for user: {user_id}")
    
    capabilities = []

    capabilities.extend(SAMPLE_capabilities)
    
    return {
        "capabilities": capabilities,
        "total": len(capabilities)
    }


@router.post("/create")
async def create_agent(request: CreateAgentRequest, user_id: str = "default"):
    """创建自定义智能体"""
    logger.info(f"[Agents] Creating agent: {request.name} by user: {user_id}")
    
    import uuid
    from datetime import datetime
    
    agent = {
        "id": f"agent_{uuid.uuid4().hex[:8]}",
        "name": request.name,
        "description": request.description,
        "system_prompt": request.system_prompt,
        "tools": request.tools,
        "capabilities": request.capabilities,
        "is_public": request.is_public,
        "created_by": user_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    return {
        "success": True,
        "agent": agent,
        "message": "Agent created successfully"
    }


@router.post("/{agent_id}/chat")
async def chat_with_agent(agent_id: str, request: Dict[str, Any]):
    """与智能体聊天"""
    logger.info(f"[Agents] Chat with agent: {agent_id}")
    
    agent = next((a for a in SAMPLE_AGENTS if a["id"] == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    message = request.get("message", "")
    
    return {
        "agent_id": agent_id,
        "agent_name": agent["name"],
        "response": f"作为{agent['name']}，我来回答你的问题：{message}\n\n[这里会根据智能体的 system_prompt 和工具生成专业的回复]",
        "timestamp": "2024-01-15T10:30:00Z"
    }


@router.get("/tools")
async def get_available_tools():
    """获取可用工具列表"""
    return {
        "tools": [
            {
                "id": "code_executor",
                "name": "代码执行器",
                "description": "执行代码并返回结果",
                "icon": "▶️"
            },
            {
                "id": "debugger",
                "name": "调试器",
                "description": "分析代码错误并提供修复建议",
                "icon": "🐛"
            },
            {
                "id": "code_explainer",
                "name": "代码解释器",
                "description": "解释代码的工作原理",
                "icon": "📖"
            },
            {
                "id": "grammar_checker",
                "name": "语法检查器",
                "description": "检查语法错误",
                "icon": "✓"
            },
            {
                "id": "vocabulary_suggester",
                "name": "词汇建议器",
                "description": "提供更高级的词汇建议",
                "icon": "📚"
            },
            {
                "id": "style_analyzer",
                "name": "风格分析器",
                "description": "分析写作风格并提供改进建议",
                "icon": "🎨"
            },
            {
                "id": "equation_solver",
                "name": "方程求解器",
                "description": "求解数学方程",
                "icon": "🧮"
            },
            {
                "id": "graph_plotter",
                "name": "图形绘制器",
                "description": "绘制数学图形",
                "icon": "📊"
            },
            {
                "id": "step_explainer",
                "name": "步骤解释器",
                "description": "逐步解释解题过程",
                "icon": "📝"
            }
        ]
    }


@router.get("/templates")
async def get_agent_templates():
    """获取智能体模板"""
    return {
        "templates": [
            {
                "id": "template_1",
                "name": "编程导师",
                "description": "教授编程语言和算法",
                "system_prompt": "你是一位{language}编程导师。你擅长用通俗易懂的语言解释编程概念，通过实例教学，并提供实用的编程建议。",
                "suggested_tools": ["code_executor", "debugger", "code_explainer"],
                "icon": "💻"
            },
            {
                "id": "template_2",
                "name": "语言学习助手",
                "description": "帮助学习外语",
                "system_prompt": "你是一位{language}学习助手。你擅长帮助学习者提高语言能力，纠正错误，并提供实用的学习建议。",
                "suggested_tools": ["grammar_checker", "vocabulary_suggester", "style_analyzer"],
                "icon": "🌍"
            },
            {
                "id": "template_3",
                "name": "学科导师",
                "description": "教授特定学科知识",
                "system_prompt": "你是一位{subject}导师。你擅长引导学生理解学科概念，而不是直接给出答案。你会用苏格拉底式提问法帮助学生自己找到答案。",
                "suggested_tools": ["step_explainer", "equation_solver"],
                "icon": "📚"
            },
            {
                "id": "template_4",
                "name": "创意写作助手",
                "description": "帮助创意写作",
                "system_prompt": "你是一位创意写作助手。你擅长激发创意，提供写作灵感，帮助改进故事情节和人物塑造。",
                "suggested_tools": ["style_analyzer", "vocabulary_suggester"],
                "icon": "✨"
            }
        ]
    }


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """获取单个智能体详情"""
    logger.debug(f"[Agents] Getting agent: {agent_id}")
    
    agent = next((a for a in SAMPLE_AGENTS if a["id"] == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    return agent


