"""
通用文本占位页（后续每个站点可以替换成真实实现）
"""

from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy


def create_simple_text_page(
    *,
    parent=None,
    title: str,
    description: str,
) -> QWidget:
    container = QWidget(parent)
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)

    title_label = QLabel(title)
    title_label.setStyleSheet(
        """
        QLabel {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        """
    )
    layout.addWidget(title_label)

    desc_label = QLabel(description)
    desc_label.setStyleSheet(
        """
        QLabel {
            font-size: 14px;
            color: #666;
            line-height: 1.5;
        }
        """
    )
    desc_label.setWordWrap(True)
    layout.addWidget(desc_label)

    layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
    return container



