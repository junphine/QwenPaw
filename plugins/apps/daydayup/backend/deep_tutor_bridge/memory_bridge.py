"""
Deep Tutor Memory Bridge
将 Deep Tutor 的三层记忆系统对接到 QwenPaw
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger("daydayup.deep_tutor")


class DeepTutorMemoryBridge:
    """
    Deep Tutor Memory 桥接器
    
    三层记忆系统：
    - L1 (Trace): 原始事件捕获，append-only JSONL
    - L2 (Document): Markdown + footnote-citation
    - L3 (Consolidated): 整合后的长期记忆
    
    Surfaces:
    - chat: 对话
    - question: 问题
    - research: 研究
    - solve: 解题
    - partner: 伙伴
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.memory_dir = data_dir / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 三层记忆存储
        self.l1_dir = self.memory_dir / "l1_trace"
        self.l2_dir = self.memory_dir / "l2_documents"
        self.l3_dir = self.memory_dir / "l3_consolidated"
        
        for d in [self.l1_dir, self.l2_dir, self.l3_dir]:
            d.mkdir(exist_ok=True)
        
        # Surfaces (记忆来源)
        self.surfaces = ["chat", "question", "research", "solve", "partner", "book"]
        
        # L3 Slots (整合后的记忆分类)
        self.l3_slots = ["profile", "concepts", "procedures", "references", "meta"]
        
        logger.info("[DeepTutorMemoryBridge] Initialized")
    
    async def add_trace(
        self,
        user_id: str,
        surface: str,
        event_type: str,
        content: Dict[str, Any]
    ) -> str:
        """
        添加 L1 Trace 事件
        
        Deep Tutor 使用 ULID 风格的 trace_id
        """
        import uuid
        
        trace_id = f"tr_{uuid.uuid4().hex[:16]}"
        timestamp = datetime.now().isoformat()
        
        trace_event = {
            "id": trace_id,
            "user_id": user_id,
            "surface": surface,
            "type": event_type,
            "content": content,
            "timestamp": timestamp
        }
        
        # 按日期和用户存储
        date_str = timestamp[:10]  # YYYY-MM-DD
        user_trace_dir = self.l1_dir / user_id / surface
        user_trace_dir.mkdir(parents=True, exist_ok=True)
        
        trace_file = user_trace_dir / f"{date_str}.jsonl"
        
        with open(trace_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(trace_event, ensure_ascii=False) + "\n")
        
        logger.debug(f"[Memory] Added trace: {trace_id}")
        
        return trace_id
    
    async def create_document(
        self,
        user_id: str,
        surface: str,
        title: str,
        content: str,
        citations: List[Dict[str, Any]] = None
    ) -> str:
        """
        创建 L2 Document
        
        Markdown 格式，支持 footnote-citation
        """
        import uuid
        
        doc_id = f"doc_{uuid.uuid4().hex[:16]}"
        timestamp = datetime.now().isoformat()
        
        # 构建 Markdown 文档
        markdown_content = f"# {title}\n\n"
        markdown_content += f"**Surface:** {surface}\n\n"
        markdown_content += f"**Created:** {timestamp}\n\n"
        markdown_content += "---\n\n"
        markdown_content += content
        
        if citations:
            markdown_content += "\n\n## References\n\n"
            for i, cite in enumerate(citations, 1):
                markdown_content += f"[{i}] {cite.get('text', '')}\n"
        
        # 保存文档
        user_doc_dir = self.l2_dir / user_id / surface
        user_doc_dir.mkdir(parents=True, exist_ok=True)
        
        doc_file = user_doc_dir / f"{doc_id}.md"
        
        with open(doc_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        logger.info(f"[Memory] Created document: {title} ({doc_id})")
        
        return doc_id
    
    async def consolidate(
        self,
        user_id: str,
        source_surface: Optional[str] = None,
        target_slot: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        整合记忆 (L1/L2 -> L3)
        
        Deep Tutor 使用 LLM 驱动的 consolidator
        """
        
        # 读取 L1 traces
        traces = await self._get_traces(user_id, source_surface)
        
        # 读取 L2 documents
        documents = await self._get_documents(user_id, source_surface)
        
        # 模拟整合过程
        consolidated = {
            "user_id": user_id,
            "source_surface": source_surface,
            "target_slot": target_slot,
            "traces_processed": len(traces),
            "documents_processed": len(documents),
            "consolidated_at": datetime.now().isoformat(),
            "summary": f"Consolidated {len(traces)} traces and {len(documents)} documents"
        }
        
        # 保存到 L3
        if target_slot:
            slot_file = self.l3_dir / user_id / f"{target_slot}.json"
            slot_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(slot_file, "w", encoding="utf-8") as f:
                json.dump(consolidated, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[Memory] Consolidated for user {user_id}")
        
        return {
            "success": True,
            "consolidated": consolidated
        }
    
    async def search(
        self,
        user_id: str,
        query: str,
        surfaces: List[str] = None,
        slots: List[str] = None
    ) -> List[Dict[str, Any]]:
        """搜索记忆"""
        
        results = []
        
        # 搜索 L2 documents
        if surfaces:
            for surface in surfaces:
                docs = await self._get_documents(user_id, surface)
                for doc in docs:
                    if query.lower() in doc.get("content", "").lower():
                        results.append({
                            "layer": "L2",
                            "type": "document",
                            "surface": surface,
                            "id": doc.get("id"),
                            "title": doc.get("title"),
                            "relevance": 0.8
                        })
        
        # 搜索 L3 slots
        if slots:
            for slot in slots:
                slot_file = self.l3_dir / user_id / f"{slot}.json"
                if slot_file.exists():
                    with open(slot_file, "r") as f:
                        data = json.load(f)
                        if query.lower() in str(data).lower():
                            results.append({
                                "layer": "L3",
                                "type": "slot",
                                "slot": slot,
                                "id": slot,
                                "relevance": 0.9
                            })
        
        return results
    
    async def _get_traces(self, user_id: str, surface: Optional[str] = None) -> List[Dict]:
        """获取 L1 traces"""
        traces = []
        
        user_dir = self.l1_dir / user_id
        if not user_dir.exists():
            return traces
        
        surfaces_to_read = [surface] if surface else self.surfaces
        
        for s in surfaces_to_read:
            surface_dir = user_dir / s
            if not surface_dir.exists():
                continue
            
            for trace_file in surface_dir.glob("*.jsonl"):
                with open(trace_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            traces.append(json.loads(line))
        
        return traces
    
    async def _get_documents(self, user_id: str, surface: Optional[str] = None) -> List[Dict]:
        """获取 L2 documents"""
        documents = []
        
        user_dir = self.l2_dir / user_id
        if not user_dir.exists():
            return documents
        
        surfaces_to_read = [surface] if surface else self.surfaces
        
        for s in surfaces_to_read:
            surface_dir = user_dir / s
            if not surface_dir.exists():
                continue
            
            for doc_file in surface_dir.glob("*.md"):
                with open(doc_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # 解析标题
                    title = content.split("\n")[0].replace("# ", "") if content.startswith("#") else doc_file.stem
                    
                    documents.append({
                        "id": doc_file.stem,
                        "surface": s,
                        "title": title,
                        "content": content
                    })
        
        return documents
    
    def get_stats(self, user_id: str) -> Dict[str, Any]:
        """获取记忆统计"""
        
        # 统计 L1
        l1_count = 0
        user_l1_dir = self.l1_dir / user_id
        if user_l1_dir.exists():
            for surface_dir in user_l1_dir.iterdir():
                if surface_dir.is_dir():
                    for trace_file in surface_dir.glob("*.jsonl"):
                        with open(trace_file, "r") as f:
                            l1_count += sum(1 for _ in f)
        
        # 统计 L2
        l2_count = 0
        user_l2_dir = self.l2_dir / user_id
        if user_l2_dir.exists():
            for surface_dir in user_l2_dir.iterdir():
                if surface_dir.is_dir():
                    l2_count += len(list(surface_dir.glob("*.md")))
        
        # 统计 L3
        l3_count = 0
        user_l3_dir = self.l3_dir / user_id
        if user_l3_dir.exists():
            l3_count = len(list(user_l3_dir.glob("*.json")))
        
        return {
            "l1_traces": l1_count,
            "l2_documents": l2_count,
            "l3_slots": l3_count,
            "surfaces": self.surfaces,
            "slots": self.l3_slots
        }
