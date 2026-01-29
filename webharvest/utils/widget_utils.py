"""
Widget工具函数
提供Widget生命周期管理和通用操作
"""

from PySide6.QtWidgets import QWidget, QLayout


def ensure_widget_valid(widget: QWidget) -> bool:
    """
    检查Widget是否有效（没有被删除）
    
    :param widget: 要检查的Widget
    :return: True表示有效，False表示已被删除
    """
    if widget is None:
        return False
    try:
        # 尝试访问widget的属性来检查是否有效
        _ = widget.sizePolicy()
        return True
    except RuntimeError:
        # widget已被删除
        return False


def safe_delete_widget(widget: QWidget):
    """
    安全地删除Widget
    
    :param widget: 要删除的Widget
    """
    if widget is None:
        return
    try:
        widget.setParent(None)
        widget.deleteLater()
    except RuntimeError:
        # widget已被删除，忽略错误
        pass


def clear_layout(layout: QLayout):
    """
    清空布局中的所有Widget
    
    :param layout: 要清空的布局
    """
    if layout is None:
        return
    
    widgets_to_delete = []
    while layout.count() > 0:
        item = layout.takeAt(0)
        if item and item.widget():
            widget = item.widget()
            widget.setParent(None)
            widgets_to_delete.append(widget)
    
    # 延迟删除widget
    from PySide6.QtCore import QTimer
    def delete_widgets():
        for w in widgets_to_delete:
            safe_delete_widget(w)
    
    QTimer.singleShot(200, delete_widgets)

