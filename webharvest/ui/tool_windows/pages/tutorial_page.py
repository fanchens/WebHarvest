from __future__ import annotations

from ._simple_text_page import create_simple_text_page


def create_tutorial_page(*, parent=None, tool_name: str = "", site_key: str = ""):
    return create_simple_text_page(
        parent=parent,
        title="使用教程",
        description="查看详细的使用指南和帮助文档。",
    )



