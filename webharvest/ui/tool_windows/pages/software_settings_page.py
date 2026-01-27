from __future__ import annotations

from ._simple_text_page import create_simple_text_page


def create_software_settings_page(*, parent=None, tool_name: str = "", site_key: str = ""):
    return create_simple_text_page(
        parent=parent,
        title="软件设置",
        description="界面主题、语言、快捷键等系统配置。",
    )


