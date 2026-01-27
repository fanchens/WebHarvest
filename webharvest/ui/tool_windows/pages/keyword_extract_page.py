from __future__ import annotations

from ._simple_text_page import create_simple_text_page


def create_keyword_extract_page(*, parent=None, tool_name: str = "", site_key: str = ""):
    return create_simple_text_page(
        parent=parent,
        title="关键词提取功能",
        description=f"站点: {site_key or 'default'}\n输入关键词进行内容搜索和提取。",
    )


