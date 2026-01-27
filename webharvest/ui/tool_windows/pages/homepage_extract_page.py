from __future__ import annotations

from ._simple_text_page import create_simple_text_page


def create_homepage_extract_page(*, parent=None, tool_name: str = "", site_key: str = ""):
    return create_simple_text_page(
        parent=parent,
        title="主页提取功能",
        description=f"站点: {site_key or 'default'}\n这里可以配置主页内容的提取设置。",
    )


