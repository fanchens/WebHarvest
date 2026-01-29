from __future__ import annotations

from ._simple_text_page import create_simple_text_page


def create_my_homepage_extract_page(*, parent=None, tool_name: str = "", site_key: str = ""):
    return create_simple_text_page(
        parent=parent,
        title="我的主页提取功能",
        description=f"站点: {site_key or 'default'}\n提取当前登录用户的主页内容。",
    )



