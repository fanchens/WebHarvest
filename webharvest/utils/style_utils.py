"""
样式工具函数
提供样式加载和应用的工具方法
"""

from PySide6.QtWidgets import QWidget


def apply_style_to_widget(widget: QWidget, style: str):
    """
    应用样式到Widget
    
    :param widget: 目标Widget
    :param style: 样式字符串
    """
    if widget and style:
        widget.setStyleSheet(style)


def merge_styles(*styles: str) -> str:
    """
    合并多个样式字符串
    
    :param styles: 样式字符串列表
    :return: 合并后的样式字符串
    """
    return "\n".join(filter(None, styles))

