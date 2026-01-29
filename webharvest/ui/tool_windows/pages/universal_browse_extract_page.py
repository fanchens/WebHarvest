from __future__ import annotations

from ._simple_text_page import create_simple_text_page


def create_universal_browse_extract_page(*, parent=None, tool_name: str = "", site_key: str = ""):
    return create_simple_text_page(
        parent=parent,
        title="万能浏览提取功能",
        description=f"站点: {site_key or 'default'}\n支持多种网站的内容自动提取。",
    )



