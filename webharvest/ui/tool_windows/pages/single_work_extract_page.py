from __future__ import annotations

from ._simple_text_page import create_simple_text_page


def create_single_work_extract_page(*, parent=None, tool_name: str = "", site_key: str = ""):
    return create_simple_text_page(
        parent=parent,
        title="单作品提取功能",
        description=f"站点: {site_key or 'default'}\n输入作品ID或URL进行单个作品提取。",
    )


