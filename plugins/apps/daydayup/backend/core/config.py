"""
配置管理
基于 Deep Tutor 的配置系统
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict

logger = logging.getLogger("daydayup")


@dataclass
class ModelConfig:
    """模型配置"""
    provider: str = "openai"
    model: str = "gpt-4"
    api_key: str = ""
    base_url: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class MemoryConfig:
    """记忆配置"""
    enabled: bool = True
    l1_max_items: int = 50
    l2_max_items: int = 200
    l3_max_items: int = 1000
    auto_consolidate: bool = True
    consolidate_interval_hours: int = 24


@dataclass
class KnowledgeConfig:
    """知识库配置"""
    enabled: bool = True
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    max_document_size: int = 10 * 1024 * 1024  # 10MB
    supported_formats: List[str] = field(default_factory=lambda: [
        "pdf", "docx", "txt", "md", "html"
    ])


@dataclass
class PartnerConfig:
    """伙伴配置"""
    enabled: bool = True
    default_personality: str = "friendly"
    max_context_turns: int = 10
    enable_voice: bool = False


@dataclass
class UIConfig:
    """UI配置"""
    language: str = "zh-CN"
    theme: str = "auto"
    sidebar_collapsed: bool = False
    font_size: str = "medium"


class Config:
    """
    配置管理器
    管理插件的所有配置
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.config_dir = data_dir / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        # 配置文件路径
        self.main_config_file = self.config_dir / "main.json"
        self.models_config_file = self.config_dir / "models.json"
        self.ui_config_file = self.config_dir / "ui.json"
        self.secrets_file = self.config_dir / ".secrets.json"
        
        # 配置缓存
        self._config: Dict[str, Any] = {}
        self._models: Dict[str, ModelConfig] = {}
        self._memory: Optional[MemoryConfig] = None
        self._knowledge: Optional[KnowledgeConfig] = None
        self._partner: Optional[PartnerConfig] = None
        self._ui: Optional[UIConfig] = None
        
        # 加载配置
        self._load_all()
    
    def _load_all(self):
        """加载所有配置"""
        self._load_main_config()
        self._load_models_config()
        self._load_ui_config()
        logger.info("[Config] All configurations loaded")
    
    def _load_main_config(self):
        """加载主配置"""
        if self.main_config_file.exists():
            try:
                with open(self.main_config_file, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
            except Exception as e:
                logger.error(f"[Config] Failed to load main config: {e}")
                self._config = self._default_main_config()
        else:
            self._config = self._default_main_config()
            self._save_main_config()
    
    def _default_main_config(self) -> Dict[str, Any]:
        """默认主配置"""
        return {
            "version": "2.0.0",
            "plugin_id": "daydayup",
            "features": {
                "memory": True,
                "partners": True,
                "knowledge_base": True,
                "co_writer": True,
                "book": True,
                "learning_space": True,
                "my_agents": True
            },
            "memory": asdict(MemoryConfig()),
            "knowledge": asdict(KnowledgeConfig()),
            "partner": asdict(PartnerConfig())
        }
    
    def _save_main_config(self):
        """保存主配置"""
        try:
            with open(self.main_config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[Config] Failed to save main config: {e}")
    
    def _load_models_config(self):
        """加载模型配置"""
        if self.models_config_file.exists():
            try:
                with open(self.models_config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._models = {
                        name: ModelConfig(**config)
                        for name, config in data.items()
                    }
            except Exception as e:
                logger.error(f"[Config] Failed to load models config: {e}")
                self._models = {"default": ModelConfig()}
        else:
            self._models = {"default": ModelConfig()}
            self._save_models_config()
    
    def _save_models_config(self):
        """保存模型配置"""
        try:
            data = {
                name: asdict(config)
                for name, config in self._models.items()
            }
            with open(self.models_config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[Config] Failed to save models config: {e}")
    
    def _load_ui_config(self):
        """加载UI配置"""
        if self.ui_config_file.exists():
            try:
                with open(self.ui_config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._ui = UIConfig(**data)
            except Exception as e:
                logger.error(f"[Config] Failed to load UI config: {e}")
                self._ui = UIConfig()
        else:
            self._ui = UIConfig()
            self._save_ui_config()
    
    def _save_ui_config(self):
        """保存UI配置"""
        try:
            with open(self.ui_config_file, "w", encoding="utf-8") as f:
                json.dump(asdict(self._ui), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[Config] Failed to save UI config: {e}")
    
    # 公共方法
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置项"""
        self._config[key] = value
        self._save_main_config()
    
    def get_model_config(self, name: str = "default") -> ModelConfig:
        """获取模型配置"""
        return self._models.get(name, ModelConfig())
    
    def set_model_config(self, name: str, config: ModelConfig):
        """设置模型配置"""
        self._models[name] = config
        self._save_models_config()
    
    def get_memory_config(self) -> MemoryConfig:
        """获取记忆配置"""
        if self._memory is None:
            data = self._config.get("memory", {})
            self._memory = MemoryConfig(**data)
        return self._memory
    
    def get_knowledge_config(self) -> KnowledgeConfig:
        """获取知识库配置"""
        if self._knowledge is None:
            data = self._config.get("knowledge", {})
            self._knowledge = KnowledgeConfig(**data)
        return self._knowledge
    
    def get_partner_config(self) -> PartnerConfig:
        """获取伙伴配置"""
        if self._partner is None:
            data = self._config.get("partner", {})
            self._partner = PartnerConfig(**data)
        return self._partner
    
    def get_ui_config(self) -> UIConfig:
        """获取UI配置"""
        return self._ui
    
    def update_ui_config(self, **kwargs):
        """更新UI配置"""
        for key, value in kwargs.items():
            if hasattr(self._ui, key):
                setattr(self._ui, key, value)
        self._save_ui_config()
    
    def is_feature_enabled(self, feature: str) -> bool:
        """检查功能是否启用"""
        features = self._config.get("features", {})
        return features.get(feature, True)
    
    def enable_feature(self, feature: str):
        """启用功能"""
        if "features" not in self._config:
            self._config["features"] = {}
        self._config["features"][feature] = True
        self._save_main_config()
    
    def disable_feature(self, feature: str):
        """禁用功能"""
        if "features" not in self._config:
            self._config["features"] = {}
        self._config["features"][feature] = False
        self._save_main_config()
