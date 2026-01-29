"""
测试页面：公共确认提示（Confirm Dialog）演示

运行方式（在 WebHarvest 目录下）：
  python .\\测试\\test_confirm_dialog_page.py

目的：
- 提供一个“公共的确认提示”封装，后续很多危险操作（删除缓存/删除Cookie/清空数据）都能复用
- 先在 测试/ 目录验证交互与文案是否符合你的要求
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QStyle


class ConfirmIcon(str, Enum):
    INFO = "info"
    WARNING = "warning"
    QUESTION = "question"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ConfirmOptions:
    """
    统一确认弹窗的配置
    - title: 弹窗标题
    - message: 主提示文案
    - detail: 可选的详细说明（多行）
    - icon: 弹窗图标类型（info/warning/question/critical）
    - ok_text/cancel_text: 按钮文案
    - default_to_cancel: 是否默认选中“取消”（推荐危险操作默认取消）
    """

    title: str = "确认操作"
    message: str = "确定要继续吗？"
    detail: str = ""
    icon: ConfirmIcon = ConfirmIcon.INFO
    ok_text: str = "确定"
    cancel_text: str = "取消"
    default_to_cancel: bool = True
    ok_icon: Optional[QIcon] = None
    cancel_icon: Optional[QIcon] = None


def confirm(parent: Optional[QWidget], options: ConfirmOptions) -> bool:
    """
    公共确认提示（可复用）
    返回 True 表示用户确认继续；False 表示取消
    """
    box = QMessageBox(parent)
    box.setWindowTitle(options.title)
    if options.icon == ConfirmIcon.INFO:
        box.setIcon(QMessageBox.Information)
    elif options.icon == ConfirmIcon.WARNING:
        box.setIcon(QMessageBox.Warning)
    elif options.icon == ConfirmIcon.CRITICAL:
        box.setIcon(QMessageBox.Critical)
    else:
        box.setIcon(QMessageBox.Question)
    box.setText(options.message)
    if options.detail:
        box.setInformativeText(options.detail)

    ok = box.addButton(options.ok_text, QMessageBox.AcceptRole)
    cancel = box.addButton(options.cancel_text, QMessageBox.RejectRole)
    # 给按钮加“标准图标”，尽量贴近你截图那种效果（绿色勾/红色叉由系统主题决定）
    try:
        style = QApplication.style()
        ok.setIcon(options.ok_icon or style.standardIcon(QStyle.SP_DialogApplyButton))
        cancel.setIcon(options.cancel_icon or style.standardIcon(QStyle.SP_DialogCancelButton))
    except Exception:
        pass

    if options.default_to_cancel:
        box.setDefaultButton(cancel)
    else:
        box.setDefaultButton(ok)

    box.setEscapeButton(cancel)
    box.setWindowModality(Qt.WindowModal)
    box.exec()
    return box.clickedButton() == ok


class ConfirmDialogDemoPage(QWidget):
    """单独可运行的测试页面"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("测试：公共确认提示（Confirm Dialog）- 图示风格")
        self.resize(900, 420)
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        title = QLabel("公共确认提示演示（用于删除缓存/清空数据等）")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        root.addWidget(title)

        desc = QLabel(
            "点击下面按钮会先弹出统一的确认提示。\n"
            "后续把这段 confirm() 封装挪到正式代码（比如 webharvest/ui/common/xxx.py）即可复用。"
        )
        desc.setStyleSheet("color: #666;")
        desc.setWordWrap(True)
        root.addWidget(desc)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        image_style_btn = QPushButton("弹出确认框（按你截图风格）")
        image_style_btn.setFixedHeight(36)
        image_style_btn.clicked.connect(self._on_image_style_clicked)
        btn_row.addWidget(image_style_btn)

        danger_btn = QPushButton("删除浏览器缓存与登录信息（演示）")
        danger_btn.setFixedHeight(36)
        danger_btn.setStyleSheet(
            "QPushButton { background: #ff6b6b; color: white; border: none; font-weight: bold; padding: 6px 12px; }"
            "QPushButton:hover { background: #ff5252; }"
        )
        danger_btn.clicked.connect(self._on_delete_cache_clicked)
        btn_row.addWidget(danger_btn)

        btn_row.addStretch(1)
        root.addLayout(btn_row)

        root.addSpacing(10)

        self.result_label = QLabel("结果：等待操作…")
        self.result_label.setStyleSheet("color: #333; font-size: 13px;")
        self.result_label.setWordWrap(True)
        root.addWidget(self.result_label)

        root.addStretch(1)

    def _on_image_style_clicked(self):
        ok = confirm(
            self,
            ConfirmOptions(
                title="DY提取作品",
                message="请确定是否要关闭程序?",
                detail="",
                icon=ConfirmIcon.INFO,  # 贴近你截图：信息图标(i)
                ok_text="确定",
                cancel_text="取消",
                default_to_cancel=True,  # 默认选中取消更安全
            ),
        )
        self.result_label.setText(f"结果：{'点击了确定' if ok else '点击了取消'}")

    def _on_delete_cache_clicked(self):
        ok = confirm(
            self,
            ConfirmOptions(
                title="确认清理",
                message="确定要删除浏览器缓存与登录信息吗？",
                detail="这属于危险操作：\n- 会清空本地保存的 Cookie 文件\n- 删除后账号会退出，需要重新登录\n\n建议：如果只是异常，可先重启软件或更换账号再考虑清理。",
                icon=ConfirmIcon.WARNING,
                ok_text="我已确认，继续删除",
                cancel_text="取消",
                default_to_cancel=True,
            ),
        )
        if not ok:
            self.result_label.setText("结果：已取消（未执行删除）")
            return

        # 这里模拟执行真实删除逻辑
        self.result_label.setText("结果：用户已确认（这里将执行删除缓存/删除 Cookie 的逻辑）")


def main():
    app = QApplication(sys.argv)
    w = ConfirmDialogDemoPage()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


