from __future__ import annotations

"""
WebView2 配置 / 缓存目录路径

目标：
- 统一 WebView2 使用的 user_data 目录
- 方便在“删除浏览器缓存与登录信息”时，一并清除浏览器侧缓存
- 支持按平台（site_key）分离目录，避免不同平台数据混叠
"""

import os
import sys
from pathlib import Path


def get_webview2_profile_dir(site_key: str | None = None) -> Path:
    """
    返回 WebView2 使用的 user_data 目录（读写都在这里）

    策略与 collectors.common.config.ProjectPaths 大致对齐：
    - 源码运行：<项目根>/data/webview2_profile[/<site_key>]
    - 打包运行：%LOCALAPPDATA%/WebHarvest/webview2_profile[/<site_key>]

    Args:
        site_key: 平台标识（如 "douyin", "xiaohongshu"），None 时返回基础目录
    """
    is_frozen = bool(getattr(sys, "frozen", False))

    if is_frozen:
        local_app_data = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if local_app_data:
            base_dir = Path(local_app_data) / "WebHarvest" / "webview2_profile"
        else:
            base_dir = Path.home() / ".WebHarvest" / "webview2_profile"
    else:
        # 源码运行：webharvest/browser -> webharvest -> WebHarvest
        root = Path(__file__).resolve().parents[2]
        base_dir = root / "data" / "webview2_profile"

    # 如果指定了 site_key，返回该平台的子目录；否则返回基础目录
    if site_key:
        return base_dir / site_key
    return base_dir


