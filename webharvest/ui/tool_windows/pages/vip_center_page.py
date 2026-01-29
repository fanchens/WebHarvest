from __future__ import annotations

from ._simple_text_page import create_simple_text_page


def create_vip_center_page(*, parent=None, tool_name: str = "", site_key: str = ""):
    return create_simple_text_page(
        parent=parent,
        title="VIP中心",
        description=f"站点: {site_key or 'default'}\n会员特权、付费功能、升级服务。",
    )



