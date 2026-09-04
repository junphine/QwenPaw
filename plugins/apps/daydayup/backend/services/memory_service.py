"""
记忆服务
管理三层记忆系统
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

from ..core.config import Config

logger = logging.getLogger("daydayup")


class MemoryService:
    """
    记忆服务
    管理三层记忆系统：L1(工作记忆)、L2(语义记忆)、L3(情景记忆)
    基于 Deep Tutor 架构
    """

    def __init__(self, data_dir: Path, config: Config):
        self.data_dir = data_dir
        self.config = config
        self.service_dir = data_dir / "memory"
        self.service_dir.mkdir(exist_ok=True)

        # 记忆存储文件
        self.l1_file = self.service_dir / "l1_traces.jsonl"  # JSONL format for append-only
        self.l2_file = self.service_dir / "l2_documents.json"
        self.l3_file = self.service_dir / "l3_consolidated.json"

        # 初始化存储文件
        self._init_storage_files()

        logger.info("[MemoryService] Initialized")

    def _init_storage_files(self):
        """初始化存储文件"""
        # L1: 工作记忆（JSONL 格式，追加-only）
        if not self.l1_file.exists():
            self.l1_file.write_text("", encoding="utf-8")

        # L2: 语义记忆（JSON 格式）
        if not self.l2_file.exists():
            self.l2_file.write_text(json.dumps([], ensure_ascii=False, indent=2), encoding="utf-8")

        # L3: 情景记忆（JSON 格式）
        if not self.l3_file.exists():
            self.l3_file.write_text(json.dumps([], ensure_ascii=False, indent=2), encoding="utf-8")

    async def startup(self):
        """启动服务"""
        logger.info("[MemoryService] Starting up...")
        # 加载现有记忆到缓存（如果需要）

    async def shutdown(self):
        """关闭服务"""
        logger.info("[MemoryService] Shutting down...")
        # 保存任何未写入的数据

    def _generate_memory_id(self, content: str) -> str:
        """生成记忆ID"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{content}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def _read_l1_traces(self) -> List[Dict[str, Any]]:
        """读取L1痕迹记忆"""
        traces = []
        if self.l1_file.exists():
            try:
                with open(self.l1_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            traces.append(json.loads(line))
            except Exception as e:
                logger.error(f"[MemoryService] Error reading L1 traces: {e}")
        return traces

    def _write_l1_trace(self, trace: Dict[str, Any]):
        """写入L1痕迹记忆"""
        try:
            with open(self.l1_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(trace, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"[MemoryService] Error writing L1 trace: {e}")

    def _read_l2_documents(self) -> List[Dict[str, Any]]:
        """读取L2语义记忆文档"""
        if self.l2_file.exists():
            try:
                with open(self.l2_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"[MemoryService] Error reading L2 documents: {e}")
        return []

    def _write_l2_documents(self, documents: List[Dict[str, Any]]):
        """写入L2语义记忆文档"""
        try:
            with open(self.l2_file, 'w', encoding='utf-8') as f:
                json.dump(documents, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[MemoryService] Error writing L2 documents: {e}")

    def _read_l3_consolidated(self) -> List[Dict[str, Any]]:
        """读取L3情景记忆"""
        if self.l3_file.exists():
            try:
                with open(self.l3_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"[MemoryService] Error reading L3 consolidated: {e}")
        return []

    def _write_l3_consolidated(self, consolidated: List[Dict[str, Any]]):
        """写入L3情景记忆"""
        try:
            with open(self.l3_file, 'w', encoding='utf-8') as f:
                json.dump(consolidated, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[MemoryService] Error writing L3 consolidated: {e}")

    def save_memory(self, content: str, layer: str = "l1", memory_type: str = "learning",
                   source: str = "user", user_id: str = "default",
                   tags: List[str] = None, importance: int = 3,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """保存记忆到指定层"""
        logger.info(f"[MemoryService] Saving memory to {layer}")

        memory_id = self._generate_memory_id(content)
        timestamp = datetime.now().isoformat()

        memory_entry = {
            "id": memory_id,
            "content": content,
            "layer": layer,
            "type": memory_type,
            "source": source,
            "user_id": user_id,
            "timestamp": timestamp,
            "tags": tags or [],
            "importance": max(1, min(5, importance)),  # 确保在1-5范围内
            "metadata": metadata or {}
        }

        if layer == "l1":
            # L1: 工作记忆 - 追加到JSONL文件
            self._write_l1_trace(memory_entry)

            # 检查L1容量限制（保持最近50条）
            traces = self._read_l1_traces()
            if len(traces) > 50:
                # 保留最新的50条
                recent_traces = traces[-50:]
                # 重写文件
                with open(self.l1_file, 'w', encoding='utf-8') as f:
                    for trace in recent_traces:
                        f.write(json.dumps(trace, ensure_ascii=False) + '\n')

        elif layer == "l2":
            # L2: 语义记忆 - 添加到JSON文档集合
            documents = self._read_l2_documents()
            # 检查是否已存在（避免重复）
            existing_ids = {doc.get("id") for doc in documents}
            if memory_id not in existing_ids:
                documents.append(memory_entry)
                # 保持L2容量限制（最近200条）
                if len(documents) > 200:
                    documents = documents[-200:]
                self._write_l2_documents(documents)

        elif layer == "l3":
            # L3: 情景记忆 - 添加到JSON文档集合
            consolidated = self._read_l3_consolidated()
            # 检查是否已存在（避免重复）
            existing_ids = {doc.get("id") for doc in consolidated}
            if memory_id not in existing_ids:
                consolidated.append(memory_entry)
                # 保持L3容量限制（最多1000条）
                if len(consolidated) > 1000:
                    consolidated = consolidated[-1000:]
                self._write_l3_consolidated(consolidated)

        return memory_id

    def search_memories(self, query: str, layers: List[str] = None,
                       limit: int = 10, tags: List[str] = None) -> List[Dict[str, Any]]:
        """搜索记忆"""
        logger.debug(f"[MemoryService] Searching memories: {query}")

        if layers is None:
            layers = ["l1", "l2", "l3"]

        results = []
        query_lower = query.lower()

        # 搜索L1层
        if "l1" in layers:
            traces = self._read_l1_traces()
            for trace in traces:
                if query_lower in trace["content"].lower():
                    if not tags or any(tag in trace["tags"] for tag in tags):
                        results.append(trace)

        # 搜索L2层
        if "l2" in layers:
            documents = self._read_l2_documents()
            for doc in documents:
                if query_lower in doc["content"].lower():
                    if not tags or any(tag in doc["tags"] for tag in tags):
                        results.append(doc)

        # 搜索L3层
        if "l3" in layers:
            consolidated = self._read_l3_consolidated()
            for mem in consolidated:
                if query_lower in mem["content"].lower():
                    if not tags or any(tag in mem["tags"] for tag in tags):
                        results.append(mem)

        # 按时间戳排序（最新的在前）
        results.sort(key=lambda x: x["timestamp"], reverse=True)

        return results[:limit]

    def consolidate_memory(self, memory_id: str, target_layer: str = "l2") -> bool:
        """整合记忆（从较低层提升到较高层）"""
        logger.info(f"[MemoryService] Consolidating memory {memory_id} to {target_layer}")

        # 定义层级顺序：l1 -> l2 -> l3
        layer_order = {"l1": 0, "l2": 1, "l3": 2}

        if target_layer not in layer_order:
            logger.error(f"[MemoryService] Invalid target layer: {target_layer}")
            return False

        target_level = layer_order[target_layer]

        # 从源层读取记忆
        source_memory = None
        source_layer = None

        # 检查L1
        if "l1" in layer_order and layer_order["l1"] < target_level:
            traces = self._read_l1_traces()
            for trace in traces:
                if trace["id"] == memory_id:
                    source_memory = trace
                    source_layer = "l1"
                    break

        # 检查L2
        if not source_memory and "l2" in layer_order and layer_order["l2"] < target_level:
            documents = self._read_l2_documents()
            for doc in documents:
                if doc["id"] == memory_id:
                    source_memory = doc
                    source_layer = "l2"
                    break

        if not source_memory:
            logger.warning(f"[MemoryService] Memory {memory_id} not found in lower layers")
            return False

        # 创建提升后的记忆（保留原始信息，更新层和时间戳）
        elevated_memory = source_memory.copy()
        elevated_memory["layer"] = target_layer
        elevated_memory["timestamp"] = datetime.now().isoformat()

        # 添加整合标记到元数据
        if "consolidation_history" not in elevated_memory["metadata"]:
            elevated_memory["metadata"]["consolidation_history"] = []
        elevated_memory["metadata"]["consolidation_history"].append({
            "from_layer": source_layer,
            "to_layer": target_layer,
            "timestamp": datetime.now().isoformat()
        })

        # 移除源层的记忆（如果是L1的话，需要重写文件）
        if source_layer == "l1":
            traces = self._read_l1_traces()
            traces = [t for t in traces if t["id"] != memory_id]
            # 重写L1文件
            with open(self.l1_file, 'w', encoding='utf-8') as f:
                for trace in traces:
                    f.write(json.dumps(trace, ensure_ascii=False) + '\n')
        elif source_layer == "l2":
            documents = self._read_l2_documents()
            documents = [d for d in documents if d["id"] != memory_id]
            self._write_l2_documents(documents)
        elif source_layer == "l3":
            consolidated = self._read_l3_consolidated()
            consolidated = [d for d in consolidated if d["id"] != memory_id]
            self._write_l3_consolidated(consolidated)

        # 添加到目标层
        if target_layer == "l1":
            self._write_l1_trace(elevated_memory)
        elif target_layer == "l2":
            documents = self._read_l2_documents()
            documents.append(elevated_memory)
            # 保持容量限制
            if len(documents) > 200:
                documents = documents[-200:]
            self._write_l2_documents(documents)
        elif target_layer == "l3":
            consolidated = self._read_l3_consolidated()
            consolidated.append(elevated_memory)
            # 保持容量限制
            if len(consolidated) > 1000:
                consolidated = consolidated[-1000:]
            self._write_l3_consolidated(consolidated)

        logger.info(f"[MemoryService] Memory {memory_id} consolidated from {source_layer} to {target_layer}")
        return True

    def auto_consolidate(self) -> Dict[str, int]:
        """自动整合记忆（基于重要性和时间）"""
        logger.info("[MemoryService] Running auto-consolidation")

        stats = {"l1_to_l2": 0, "l2_to_l3": 0}

        # L1 -> L2: 重要性>=4且超过一定时间的记忆
        traces = self._read_l1_traces()
        now = datetime.now()

        for trace in traces:
            # 检查是否应该整合到L2
            importance = trace.get("importance", 3)
            try:
                mem_time = datetime.fromisoformat(trace["timestamp"].replace('Z', '+00:00'))
                hours_old = (now - mem_time.replace(tzinfo=None)).total_seconds() / 3600
            except:
                hours_old = 24  # 默认超过24小时

            if importance >= 4 and hours_old > 1:  # 重要且超过1小时
                if self.consolidate_memory(trace["id"], "l2"):
                    stats["l1_to_l2"] += 1

        # L2 -> L3: 重要性>=5且超过一定时间的记忆
        documents = self._read_l2_documents()

        for doc in documents:
            # 检查是否应该整合到L3
            importance = doc.get("importance", 3)
            try:
                mem_time = datetime.fromisoformat(doc["timestamp"].replace('Z', '+00:00'))
                hours_old = (now - mem_time.replace(tzinfo=None)).total_seconds() / 3600
            except:
                hours_old = 168  # 默认超过1周（7*24）

            if importance >= 5 and hours_old > 168:  # 非常重要且超过1周
                if self.consolidate_memory(doc["id"], "l3"):
                    stats["l2_to_l3"] += 1

        logger.info(f"[MemoryService] Auto-consolidation completed: {stats}")
        return stats

    def get_stats(self) -> Dict[str, Any]:
        """获取记忆统计"""
        l1_traces = self._read_l1_traces()
        l2_documents = self._read_l2_documents()
        l3_consolidated = self._read_l3_consolidated()

        return {
            "l1_count": len(l1_traces),
            "l2_count": len(l2_documents),
            "l3_count": len(l3_consolidated),
            "l1_capacity": 50,
            "l2_capacity": 200,
            "l3_capacity": 1000,
            "l1_usage": (len(l1_traces) / 50) * 100 if l1_traces else 0,
            "l2_usage": (len(l2_documents) / 200) * 100 if l2_documents else 0,
            "l3_usage": (len(l3_consolidated) / 1000) * 100 if l3_consolidated else 0
        }

    def get_recent_memories(self, limit: int = 10, layer: str = None) -> List[Dict[str, Any]]:
        """获取最近的记忆"""
        results = []

        if layer == "l1" or layer is None:
            traces = self._read_l1_traces()
            results.extend(traces)

        if layer == "l2" or layer is None:
            documents = self._read_l2_documents()
            results.extend(documents)

        if layer == "l3" or layer is None:
            consolidated = self._read_l3_consolidated()
            results.extend(consolidated)

        # 按时间戳排序（最新的在前）
        results.sort(key=lambda x: x["timestamp"], reverse=True)

        return results[:limit]