from __future__ import annotations

from dataclasses import dataclass
import os
import sys
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    """
    项目路径约定（统一管理输出/缓存/日志目录）
    """

    root: Path

    @staticmethod
    def detect() -> "ProjectPaths":
        """
        路径策略（对齐根 README 的“安装目录/用户数据目录”要求）：
        - 源码运行：默认使用项目根目录下的 data/
        - 打包运行（PyInstaller/冻结）：默认使用用户可写目录（如 %LOCALAPPDATA%\\WebHarvest\\data）
        """
        is_frozen = bool(getattr(sys, "frozen", False))

        if is_frozen:
            # Windows 优先使用 LOCALAPPDATA
            local_app_data = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
            if local_app_data:
                root = Path(local_app_data) / "WebHarvest"
                return ProjectPaths(root=root)

        # webharvest/collectors/common -> webharvest -> WebHarvest（源码运行兜底）
        root = Path(__file__).resolve().parents[3]
        return ProjectPaths(root=root)

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    @property
    def outputs_dir(self) -> Path:
        return self.data_dir / "outputs"

    @property
    def logs_dir(self) -> Path:
        return self.data_dir / "logs"

    @property
    def cookies_dir(self) -> Path:
        return self.data_dir / "cookies"

    def ensure(self) -> "ProjectPaths":
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
        return self


@dataclass
class CollectorConfig:
    """
    采集通用配置（站点可覆盖）
    """

    site_key: str = "unknown"

    # 运行节奏/封控相关
    min_sleep_s: float = 0.2
    max_sleep_s: float = 1.0

    # 重试相关
    max_retries: int = 3
    base_backoff_s: float = 0.5

    # 限流相关
    qps: float = 0.8  # 每秒最多触发多少次“动作/请求”（粗粒度）

    # 输出相关
    output_subdir: str = ""  # 为空则使用 site_key


