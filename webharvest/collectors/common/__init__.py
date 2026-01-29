"""
采集公共能力（Collectors Common）

这里放所有站点都能复用的能力层：
- 配置：CollectorConfig
- 路径：ProjectPaths
- 保存：Storage（JSON/JSONL）
- 日志：get_logger
- 重试：retry
- 限流：RateLimiter
- 封控/反检测：AntiDetection（UA/headers/节奏）
"""

from .config import CollectorConfig, ProjectPaths
from .logger import get_logger
from .rate_limit import RateLimiter
from .retry import retry
from .storage import (
    CsvStorage,
    DataExporter,
    ExcelStorage,
    JsonlStorage,
    JsonStorage,
    SaveFormat,
    TxtStorage,
)

__all__ = [
    "CollectorConfig",
    "ProjectPaths",
    "get_logger",
    "RateLimiter",
    "retry",
    "JsonStorage",
    "JsonlStorage",
    "CsvStorage",
    "ExcelStorage",
    "TxtStorage",
    "DataExporter",
    "SaveFormat",
]


