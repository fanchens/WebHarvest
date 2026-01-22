"""
左侧菜单面板组件
提供可复用的菜单面板控件，支持动态菜单项和点击事件
"""

from typing import List, Optional

from PySide6.QtCore import Qt, Signal, QEventLoop, QPoint
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
)

# ===================== 左侧面板相关常量 ======================
# 面板尺寸常量
LEFT_PANEL_WIDTH = 220

# 面板样式
LEFT_PANEL_STYLE = """
LeftMenuPanel { background: #f7f8fa !important; }
QLabel#menu-item {
    padding: 12px 16px;
    border-bottom: 1px solid #e6e8eb;
    color: #2c3e50;
    background: #f7f8fa;
}
QLabel#menu-item:hover { background: #e7f1ff; }
QLabel#menu-item[selected="true"] {
    background: #d6e9ff;
    color: #1f6fb2;
    font-weight: bold;
}
"""

# 默认菜单项
DEFAULT_MENU_ITEMS = [
    "作品列表", "主页提取", "单作品提取", "关键词提取", "我的主页提取",
    "万能浏览提取", "下载设置", "VIP中心", "浏览器_登录", "软件设置",
    "推送消息", "语音转写文案", "使用教程",
]


class LeftMenuPanel(QWidget):
    """左侧菜单面板组件"""

    # 信号定义
    menu_item_clicked = Signal(int)  # 发送菜单项索引

    def __init__(self, menu_items: Optional[List[str]] = None, parent=None):
        super().__init__(parent)

        # 初始化属性
        self.menu_items = menu_items or DEFAULT_MENU_ITEMS
        self.menu_labels: List[QLabel] = []
        self.current_menu_index = 0

        # 设置基本属性
        self.setFixedWidth(LEFT_PANEL_WIDTH)
        self.setStyleSheet(LEFT_PANEL_STYLE)

        # 创建UI
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 创建菜单项
        for idx, name in enumerate(self.menu_items):
            label = QLabel(name)
            label.setObjectName("menu-item")
            label.setProperty("selected", "true" if idx == 0 else "false")
            label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # 连接点击事件
            label.mouseReleaseEvent = lambda event, i=idx: self._on_menu_clicked(i)

            layout.addWidget(label, 1)  # stretch factor 1
            self.menu_labels.append(label)

    def _on_menu_clicked(self, index: int):
        """菜单项点击处理"""
        if not (0 <= index < len(self.menu_labels)) or index == self.current_menu_index:
            return

        self._set_selected(index)
        self.menu_item_clicked.emit(index)  # 发送信号

    def _set_selected(self, index: int):
        """设置菜单项选中状态"""
        # 批量更新样式
        self.current_menu_index = index
        for i, label in enumerate(self.menu_labels):
            label.setProperty("selected", "true" if i == index else "false")

        # 处理事件队列
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents(QEventLoop.AllEvents)

        # 刷新样式
        for label in self.menu_labels:
            label.style().unpolish(label)
            label.style().polish(label)

    def set_menu_items(self, menu_items: List[str]):
        """动态设置菜单项"""
        self.menu_items = menu_items

        # 清除现有菜单
        for label in self.menu_labels:
            label.setParent(None)
        self.menu_labels.clear()

        # 重新创建菜单
        layout = self.layout()
        for idx, name in enumerate(self.menu_items):
            label = QLabel(name)
            label.setObjectName("menu-item")
            label.setProperty("selected", "false")
            label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # 连接点击事件
            label.mouseReleaseEvent = lambda event, i=idx: self._on_menu_clicked(i)

            layout.addWidget(label, 1)
            self.menu_labels.append(label)

        # 默认选中第一个
        if self.menu_labels:
            self._set_selected(0)

    def get_current_menu_item(self) -> Optional[str]:
        """获取当前选中的菜单项文本"""
        if 0 <= self.current_menu_index < len(self.menu_items):
            return self.menu_items[self.current_menu_index]
        return None

    def get_current_menu_index(self) -> int:
        """获取当前选中的菜单项索引"""
        return self.current_menu_index

    def set_selected_index(self, index: int):
        """设置选中的菜单项"""
        if 0 <= index < len(self.menu_labels):
            self._set_selected(index)

    def add_menu_item(self, name: str):
        """添加菜单项"""
        self.menu_items.append(name)

        # 创建新的标签
        idx = len(self.menu_labels)
        label = QLabel(name)
        label.setObjectName("menu-item")
        label.setProperty("selected", "false")
        label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 连接点击事件
        label.mouseReleaseEvent = lambda event, i=idx: self._on_menu_clicked(i)

        self.layout().addWidget(label, 1)
        self.menu_labels.append(label)

    def remove_menu_item(self, index: int):
        """移除菜单项"""
        if 0 <= index < len(self.menu_labels):
            # 移除标签
            label = self.menu_labels.pop(index)
            label.setParent(None)

            # 移除菜单项文本
            self.menu_items.pop(index)

            # 调整当前选中索引
            if self.current_menu_index >= index:
                self.current_menu_index = max(0, self.current_menu_index - 1)

            # 重新设置选中状态
            if self.menu_labels:
                self._set_selected(self.current_menu_index)
