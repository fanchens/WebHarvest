from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout

from ..component.data_table_widget import DataTableWidget


def _get_schema(site_key: str) -> tuple[list[str] | None, list[int] | None]:
    """按站点返回作品列表动态列（不含：选择/序号两列）"""
    site = (site_key or "").lower()

    if site == "douyin":
        return (
            ["作品ID", "抖音作品标题", "作者", "播放量", "点赞", "状态"],
            [110, 240, 140, 110, 100, 100],
        )

    if site == "xiaohongshu":
        return (
            ["作品ID", "红薯作品标题", "作者", "点赞", "收藏", "评论", "状态"],
            [110, 240, 140, 100, 100, 100, 100],
        )

    if site == "kuaishou":
        return (
            ["作品ID", "快手作品标题", "作者", "播放量", "点赞", "评论", "状态"],
            [110, 240, 140, 110, 100, 100, 100],
        )

    return (None, None)


def create_works_list_page(*, parent=None, tool_name: str = "", site_key: str = "") -> QWidget:
    container = QWidget(parent)
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)

    extra_headers, extra_widths = _get_schema(site_key)
    if extra_headers is None:
        table = DataTableWidget(parent=container)
    else:
        table = DataTableWidget(parent=container, extra_headers=extra_headers, extra_widths=extra_widths)
    layout.addWidget(table)
    return container


