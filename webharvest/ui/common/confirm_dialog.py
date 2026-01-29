"""
公共确认弹窗（Confirm Dialog）

目标：
- 统一“危险操作”的确认提示样式与交互
- 复用在：删除缓存/清空 Cookie/删除文件/批量删除等场景

说明：
- 基于 Qt 的 QMessageBox，使用系统标准图标/按钮图标，风格接近你截图那种效果
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import html

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox, QStyle, QWidget


class ConfirmIcon(str, Enum):
    INFO = "info"
    WARNING = "warning"
    QUESTION = "question"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ConfirmOptions:
    """
    统一确认弹窗配置
    - title: 弹窗标题
    - message: 主提示文案
    - detail: 可选详细说明（多行）
    - icon: 弹窗图标类型
    - ok_text/cancel_text: 按钮文案
    - default_to_cancel: 是否默认选中取消（危险操作建议 True）
    - ok_icon/cancel_icon: 可选自定义按钮图标（默认用 Qt 标准图标）
    """

    title: str = "确认操作"
    message: str = "确定要继续吗？"
    detail: str = ""
    icon: ConfirmIcon = ConfirmIcon.INFO
    ok_text: str = "确定"
    cancel_text: str = "取消"
    default_to_cancel: bool = True
    ok_icon: QIcon | None = None
    cancel_icon: QIcon | None = None


def confirm(parent: QWidget | None, options: ConfirmOptions) -> bool:
    """
    公共确认提示（可复用）
    返回 True 表示用户确认继续；False 表示取消
    """
    box = QMessageBox(parent)
    box.setWindowTitle(options.title)

    # 统一基础尺寸，避免同一类弹窗时大小忽大忽小
    box.setMinimumWidth(380)

    if options.icon == ConfirmIcon.INFO:
        box.setIcon(QMessageBox.Information)
    elif options.icon == ConfirmIcon.WARNING:
        box.setIcon(QMessageBox.Warning)
    elif options.icon == ConfirmIcon.CRITICAL:
        box.setIcon(QMessageBox.Critical)
    else:
        box.setIcon(QMessageBox.Question)

    # 统一用富文本，避免全局样式把文字“染白看不见”
    # detail 使用 white-space: pre-line 保留换行
    message_html = html.escape(options.message or "")
    detail_html = html.escape(options.detail or "")

    html_parts = [f"<div style='color:#333333;font-size:13px;'>{message_html}</div>"]
    if detail_html:
        html_parts.append(
            "<div style='margin-top:6px;color:#666666;font-size:12px;white-space:pre-line;'>"
            f"{detail_html}"
            "</div>"
        )

    box.setText("".join(html_parts))

    ok_btn = box.addButton(options.ok_text, QMessageBox.AcceptRole)
    cancel_btn = box.addButton(options.cancel_text, QMessageBox.RejectRole)

    # 按钮标准图标：尽量贴近“确定/取消带图标”的效果
    try:
        style = QApplication.style()
        ok_btn.setIcon(options.ok_icon or style.standardIcon(QStyle.SP_DialogApplyButton))
        cancel_btn.setIcon(options.cancel_icon or style.standardIcon(QStyle.SP_DialogCancelButton))
    except Exception:
        pass

    if options.default_to_cancel:
        box.setDefaultButton(cancel_btn)
    else:
        box.setDefaultButton(ok_btn)

    box.setEscapeButton(cancel_btn)
    box.setWindowModality(Qt.WindowModal)
    box.exec()
    return box.clickedButton() == ok_btn


