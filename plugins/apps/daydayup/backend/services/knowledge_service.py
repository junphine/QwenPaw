"""
知识服务
管理知识库和文档
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import mimetypes

from ..core.config import Config

logger = logging.getLogger("daydayup")


class KnowledgeService:
    """
    知识服务
    管理知识库、文档和搜索
    """

    def __init__(self, data_dir: Path, config: Config):
        self.data_dir = data_dir
        self.config = config
        self.service_dir = data_dir / "knowledge"
        self.service_dir.mkdir(exist_ok=True)

        # 知识库存储目录
        self.bases_dir = self.service_dir / "bases"
        self.bases_dir.mkdir(exist_ok=True)

        # 索引文件
        self.index_file = self.service_dir / "index.json"

        # 初始化存储
        self._init_storage()

        logger.info("[KnowledgeService] Initialized")

    def _init_storage(self):
        """初始化存储"""
        if not self.index_file.exists():
            self.index_file.write_text(json.dumps({}, ensure_ascii=False, indent=2), encoding="utf-8")

    async def startup(self):
        """启动服务"""
        logger.info("[KnowledgeService] Starting up...")
        # 加载知识库索引到内存

    async def shutdown(self):
        """关闭服务"""
        logger.info("[KnowledgeService] Shutting down...")
        # 保存索引

    def _load_index(self) -> Dict[str, Any]:
        """加载知识库索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"[KnowledgeService] Error loading index: {e}")
        return {}

    def _save_index(self, index: Dict[str, Any]):
        """保存知识库索引"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[KnowledgeService] Error saving index: {e}")

    def _generate_id(self, content: str) -> str:
        """生成ID"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{content}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def _get_file_hash(self, file_path: Path) -> str:
        """获取文件哈希值"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            logger.error(f"[KnowledgeService] Error reading file {file_path}: {e}")
            return ""

    def create_base(self, name: str, description: str, owner_id: str = "default",
                   is_public: bool = False, tags: List[str] = None) -> str:
        """创建知识库"""
        logger.info(f"[KnowledgeService] Creating base: {name}")

        base_id = self._generate_id(name)
        timestamp = datetime.now().isoformat()

        base = {
            "id": base_id,
            "name": name,
            "description": description,
            "owner_id": owner_id,
            "is_public": is_public,
            "tags": tags or [],
            "created_at": timestamp,
            "updated_at": timestamp,
            "document_count": 0,
            "total_size": 0,
            "documents": []  # 存储文档ID列表
        }

        # 保存知识库信息
        base_dir = self.bases_dir / base_id
        base_dir.mkdir(exist_ok=True)

        base_file = base_dir / "base_info.json"
        with open(base_file, 'w', encoding='utf-8') as f:
            json.dump(base, f, ensure_ascii=False, indent=2)

        # 更新索引
        index = self._load_index()
        index["bases"][base_id] = {
            "name": name,
            "owner_id": owner_id,
            "created_at": timestamp,
            "document_count": 0
        }
        self._save_index(index)

        logger.info(f"[KnowledgeService] Base created with ID: {base_id}")
        return base_id

    def get_base(self, base_id: str) -> Optional[Dict[str, Any]]:
        """获取知识库信息"""
        logger.debug(f"[KnowledgeService] Getting base: {base_id}")
        base_file = self.bases_dir / base_id / "base_info.json"
        if base_file.exists():
            try:
                with open(base_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"[KnowledgeService] Error reading base {base_id}: {e}")
        return None

    def get_bases(self, user_id: str = "default", include_public: bool = True) -> List[Dict[str, Any]]:
        """获取知识库列表"""
        logger.debug("[KnowledgeService] Getting knowledge bases")
        index = self._load_index()
        bases = []

        for base_id, base_info in index.get("bases", {}).items():
            # 过滤条件：公开的知识库或属于用户的知识库
            if include_public and base_info.get("is_public", False):
                bases.append(base_info)
            elif not include_public and base_info.get("owner_id") == user_id:
                bases.append(base_id)

        # 获取完整的知识库信息
        result = []
        for base_info in bases:
            base_id = base_info.get("id") if isinstance(base_info, dict) and "id" in base_info else base_info
            base = self.get_base(base_id)
            if base:
                result.append(base)

        return result

    def search(self, query: str, base_ids: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索知识"""
        logger.info(f"[KnowledgeService] Searching: {query}")

        if not query.strip():
            return []

        query_lower = query.lower()
        results = []

        # 获取要搜索的知识库列表
        if base_ids is None:
            accessible_bases = self.get_bases()
            base_ids = [base["id"] for base in accessible_bases]
        else:
            # 验证访问权限
            accessible_bases = self.get_bases()
            accessible_ids = {base["id"] for base in accessible_bases}
            base_ids = [bid for bid in base_ids if bid in accessible_ids]

        # 在每个知识库中搜索
        for base_id in base_ids:
            base_results = self._search_in_base(base_id, query_lower, limit)
            results.extend(base_results)

        # 按相关性排序并限制结果数量
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:limit]

    def _search_in_base(self, base_id: str, query: str, limit: int) -> List[Dict[str, Any]]:
        """在特定知识库中搜索"""
        base_dir = self.bases_dir / base_id
        if not base_dir.exists():
            return []

        results = []
        documents_dir = base_dir / "documents"
        if not documents_dir.exists():
            return results

        # 搜索所有文档
        for doc_file in documents_dir.glob("*.json"):
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    doc = json.load(f)

                # 简单的文本匹配搜索
                content = doc.get("content", "").lower()
                title = doc.get("title", "").lower()

                score = 0
                if query in title:
                    score += 0.8  # 标题匹配给高分
                if query in content:
                    # 计算词频
                    words = content.split()
                    matches = sum(1 for word in words if query in word)
                    score += min(0.5, matches * 0.1)  # 内容匹配给较低分

                if score > 0:
                    # 提取匹配的片段
                    content_snippet = self._extract_snippet(doc.get("content", ""), query)
                    title_snippet = self._extract_snippet(doc.get("title", ""), query)

                    results.append({
                        "document_id": doc.get("id"),
                        "base_id": base_id,
                        "title": doc.get("title"),
                        "content_snippet": content_snippet,
                        "title_snippet": title_snippet,
                        "score": score,
                        "file_type": doc.get("file_type"),
                        "created_at": doc.get("created_at")
                    })

            except Exception as e:
                logger.error(f"[KnowledgeService] Error searching document {doc_file}: {e}")

        return results

    def _extract_snippet(self, text: str, query: str, context_length: int = 100) -> str:
        """提取查询词周围的文本片段"""
        if not text or not query:
            return text[:context_length]

        text_lower = text.lower()
        query_lower = query.lower()
        pos = text_lower.find(query_lower)

        if pos == -1:
            return text[:context_length]

        start = max(0, pos - context_length // 2)
        end = min(len(text), pos + len(query) + context_length // 2)

        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

        return snippet

    def add_document(self, base_id: str, file_path: Path,
                    title: str = None, description: str = None) -> str:
        """添加文档到知识库"""
        logger.info(f"[KnowledgeService] Adding document to base {base_id}: {file_path.name}")

        base = self.get_base(base_id)
        if not base:
            logger.error(f"[KnowledgeService] Base not found: {base_id}")
            return ""

        if not file_path.exists():
            logger.error(f"[KnowledgeService] File not found: {file_path}")
            return ""

        # 生成文档ID
        doc_id = self._generate_id(file_path.name)
        timestamp = datetime.now().isoformat()

        # 获取文件信息
        file_size = file_path.stat().st_size
        file_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        file_hash = self._get_file_hash(file_path)

        # 读取文件内容（对于文本文件）
        content = ""
        if file_type.startswith("text/") or file_path.suffix.lower() in [".txt", ".md", ".json", ".csv", ".xml", ".html"]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 如果UTF-8失败，尝试其他编码
                try:
                    with open(file_path, 'r', encoding='gbk') as f:
                        content = f.read()
                except:
                    content = f"[Binary file: {file_path.name}]"
        else:
            content = f"[Binary file: {file_path.name}]"

        document = {
            "id": doc_id,
            "base_id": base_id,
            "title": title or file_path.stem,
            "description": description or "",
            "content": content,
            "file_type": file_type,
            "file_size": file_size,
            "file_hash": file_hash,
            "original_filename": file_path.name,
            "created_at": timestamp,
            "updated_at": timestamp
        }

        # 保存文档
        base_dir = self.bases_dir / base_id
        documents_dir = base_dir / "documents"
        documents_dir.mkdir(exist_ok=True)

        doc_file = documents_dir / f"{doc_id}.json"
        with open(doc_file, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)

        # 更新知识库信息
        base["document_count"] = base.get("document_count", 0) + 1
        base["total_size"] = base.get("total_size", 0) + file_size
        base["updated_at"] = timestamp
        if "documents" not in base:
            base["documents"] = []
        base["documents"].append(doc_id)

        # 保存更新后的知识库信息
        base_file = base_dir / "base_info.json"
        with open(base_file, 'w', encoding='utf-8') as f:
            json.dump(base, f, ensure_ascii=False, indent=2)

        # 更新索引
        index = self._load_index()
        if base_id in index.get("bases", {}):
            index["bases"][base_id]["document_count"] = base["document_count"]
            index["bases"][base_id]["updated_at"] = timestamp
        self._save_index(index)

        logger.info(f"[KnowledgeService] Document added with ID: {doc_id}")
        return doc_id

    def get_document(self, base_id: str, document_id: str) -> Optional[Dict[str, Any]]:
        """获取文档详情"""
        logger.debug(f"[KnowledgeService] Getting document: {document_id} from base {base_id}")

        base_dir = self.bases_dir / base_id
        doc_file = base_dir / "documents" / f"{document_id}.json"

        if doc_file.exists():
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"[KnowledgeService] Error reading document {document_id}: {e}")
        return None

    def ask(self, question: str, base_ids: List[str] = None) -> Dict[str, Any]:
        """基于知识库问答"""
        logger.info(f"[KnowledgeService] Asking: {question}")

        # 首先进行搜索
        search_results = self.search(question, base_ids, limit=5)

        if not search_results:
            return {
                "question": question,
                "answer": "抱歉，我在知识库中没有找到相关信息。",
                "sources": [],
                "confidence": 0.0
            }

        # 生成回答（这里使用简单的模板，实际应用中可以使用LLM）
        answer_parts = []
        sources = []

        for result in search_results[:3]:  # 使用前3个最相关的结果
            answer_parts.append(f"根据《{result.get('title', '未知文档')}》：")
            answer_parts.append(result.get("content_snippet", ""))
            sources.append({
                "document_id": result.get("document_id"),
                "base_id": result.get("base_id"),
                "title": result.get("title"),
                "relevance": result.get("score", 0),
                "snippet": result.get("content_snippet", "")
            })

        answer = "\n\n".join(answer_parts)
        if not answer.strip():
            answer = "我在知识库中找到了一些相关信息，但无法生成完整的回答。"

        # 计算置信度（基于搜索结果的质量和数量）
        avg_score = sum(r.get("score", 0) for r in search_results) / len(search_results) if search_results else 0
        confidence = min(0.95, 0.5 + avg_score * 0.5)  # 基础置信度0.5，根据得分调整

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "search_results_count": len(search_results)
        }

    def delete_document(self, base_id: str, document_id: str) -> bool:
        """删除文档"""
        logger.info(f"[KnowledgeService] Deleting document: {document_id} from base {base_id}")

        base_dir = self.bases_dir / base_id
        doc_file = base_dir / "documents" / f"{document_id}.json"

        if not doc_file.exists():
            logger.warning(f"[KnowledgeService] Document not found: {document_id}")
            return False

        try:
            # 读取文档信息以更新知识库统计
            with open(doc_file, 'r', encoding='utf-8') as f:
                document = json.load(f)

            # 删除文档文件
            doc_file.unlink()

            # 更新知识库信息
            base = self.get_base(base_id)
            if base:
                base["document_count"] = max(0, base.get("document_count", 0) - 1)
                base["total_size"] = max(0, base.get("total_size", 0) - document.get("file_size", 0))
                base["updated_at"] = datetime.now().isoformat()
                if "documents" in base and document_id in base["documents"]:
                    base["documents"].remove(document_id)

                # 保存更新后的知识库信息
                base_file = base_dir / "base_info.json"
                with open(base_file, 'w', encoding='utf-8') as f:
                    json.dump(base, f, ensure_ascii=False, indent=2)

                # 更新索引
                index = self._load_index()
                if base_id in index.get("bases", {}):
                    index["bases"][base_id]["document_count"] = base["document_count"]
                    index["bases"][base_id]["updated_at"] = base["updated_at"]
                self._save_index(index)

            logger.info(f"[KnowledgeService] Document {document_id} deleted successfully")
            return True

        except Exception as e:
            logger.error(f"[KnowledgeService] Error deleting document {document_id}: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """获取知识服务统计"""
        index = self._load_index()
        bases = index.get("bases", {})

        total_documents = 0
        total_size = 0

        for base_info in bases.values():
            total_documents += base_info.get("document_count", 0)
            # 注意：这里的total_size需要从实际的知识库信息中获取，为了简化，我们使用估算值
            total_size += base_info.get("document_count", 0) * 102400  # 假设平均每个文档100KB

        return {
            "total_bases": len(bases),
            "total_documents": total_documents,
            "total_size": total_size,
            "total_size_formatted": f"{total_size / 1024 / 1024:.2f} MB" if total_size > 0 else "0.00 MB"
        }