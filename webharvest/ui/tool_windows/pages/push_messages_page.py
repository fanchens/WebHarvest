from __future__ import annotations

from ._simple_text_page import create_simple_text_page


def create_push_messages_page(*, parent=None, tool_name: str = "", site_key: str = ""):
    return create_simple_text_page(
        parent=parent,
        title="推送消息",
        description="配置消息推送渠道和通知设置。",
    )



