from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class XHSConfig:
    """
    小红书站点配置（后续可扩展：登录判断、选择器、API 路由等）
    """

    site_key: str = "xiaohongshu"
    base_url: str = "https://www.xiaohongshu.com"
    # 建议用户登录入口：首页/发现页会跳转到登录弹窗
    login_url: str = "https://www.xiaohongshu.com/explore"



