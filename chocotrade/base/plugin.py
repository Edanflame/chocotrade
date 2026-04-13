""""""
from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic_settings import BaseSettings

from ..config.config import settings

# 全局配置文件路径
CHOCO_ENV_FILE = settings.env_path

keyring = ""

PLUGINS = {
    "tushare": {
        "name": "tushare",
        "title": "Tushare Interface",
        "desc": "Professional data gateway for Chinese A-shares, funds, and derivatives markets.",
        "category": "data_source",
        "class": "TushareDataSource",
        "auth_fields": ["token"],
        "module_path": ["datasource","tushare_datasource"],
        "star": "5",
        "download": "100",
        "is_new": False
    },
    "okx": {
        "name": "okx",
        "title": "Okx Execution Gateway",
        "desc": "Direct market access through proprietary low-latency\
            WebSocket and REST interfaces.",
        "category": "hub",
        "class": "",
        "auth_fields": [],
        "module_path": [],
        "star": "5",
        "download": "100",
        "is_new": False,
    },
    "standard-llm": {
        "name": "standard-llm",
        "title": "Standard LLM Interface",
        "desc": "Universal LLM connector compatible with OpenAI-style APIs,\
            supporting custom endpoints and model selection.",
        "category": "robot",
        "class": "LLMCore",
        "auth_fields": ["base_url", "model_name", "api_key"],
        "module_path": ["llm", "llm"],
        "star": "5",
        "download": "500",
        "is_new": True,
    },
    "timescaledb": {
        "name": "timescaledb",
        "title": "TimescaleDB Interface",
        "desc": "High-performance time-series database optimization for\
            tick-level data storage and retrieval.",
        "category": "database",
        "class": "",
        "auth_fields": [],
        "module_path": [],
        "star": "5",
        "download": "100",
        "is_new": False,
    },
    "redis": {
        "name": "redis",
        "title": "Redis Latency Buffer",
        "desc": "In-memory data structure store for rapid order execution feedback loops.",
        "category": "memory",
        "class": "",
        "auth_fields": [],
        "module_path": [],
        "star": "4.9",
        "download": "1.2k",
        "is_new": True,
    },
    "aws_s3": {
        "name": "aws_s3",
        "title": "AWS S3 Cold Storage",
        "desc": "Automated archiving of historical trading data and\
            backtest results to the cloud.",
        "category": "cloud_upload",
        "class": "",
        "auth_fields": [],
        "module_path": [],
        "star": "4.7",
        "download": "842",
        "is_new": False,
    },
    "sentinel_bot": {
        "name": "sentinel_bot",
        "title": "Vault Sentinel Bot",
        "desc": "Receive real-time alerts and manage active positions\
            via Telegram's secure interface.",
        "category": "send",
        "class": "",
        "auth_fields": [],
        "module_path": [],
        "star": "5.0",
        "download": "2.1k",
        "is_new": False,
    },
    "polygon": {
        "name": "polygon",
        "title": "Polygon.io Stream",
        "desc": "Institutional-grade market data feed for equities, forex, and crypto markets.",
        "category": "timeline",
        "class": "",
        "auth_fields": [],
        "module_path": [],
        "star": "4.8",
        "download": "1.5k",
        "is_new": False,
    }
}


ConfigT = TypeVar("ConfigT", bound=BaseSettings)


class BasePlugin[ConfigT](ABC):
    """"""
    SERVICE_NAME = "chocotrade"
    config_class: type[ConfigT]

    def __init__(self):
        """"""
        self.config: ConfigT = self.config_class()
        self.plugin_name = self.__class__.__name__.replace("Plugin", "").upper()
        print(f"初始化插件: {self.plugin_name}")

    def get_from_keyring(self, key: str):
        """"""
        try:
            kr_val = keyring.get_password(self.SERVICE_NAME, key.upper())
            return kr_val
        except Exception:
            pass

    def _update_from_keyring(self, key: str, value: str):
        """"""
        try:
            keyring.set_password(self.SERVICE_NAME, key.upper(), value)
        except Exception:
            pass

    def _remove_from_keyring(self, key: str):
        try:
            keyring.delete_password(self.SERVICE_NAME, key)
        except Exception:
            pass

    @abstractmethod
    def start(self):
        pass
