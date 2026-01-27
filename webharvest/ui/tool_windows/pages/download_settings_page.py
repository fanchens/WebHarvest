from __future__ import annotations

from ._simple_text_page import create_simple_text_page


def create_download_settings_page(*, parent=None, tool_name: str = "", site_key: str = ""):
    return create_simple_text_page(
        parent=parent,
        title="下载设置",
        description=f"站点: {site_key or 'default'}\n配置下载路径、并发数、速度限制等。",
    )


