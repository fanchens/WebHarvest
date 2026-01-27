"""
工具窗口主框架 - 模块化版本

说明：
- 左侧菜单按 site_key 动态生成（可隐藏某些菜单项，但不删除页面）
- 右侧内容通过 site_profiles.py 的 page_factories 创建，对应 pages/ 目录
"""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

from .left_menu_panel import LeftMenuPanel
from .right_content_panel import RightContentPanel
from .site_profiles import get_site_profile

# ===================== 窗口配置常量 ======================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800


class CheckboxTestWindow(QMainWindow):
    """工具窗口 - 使用模块化组件"""

    def __init__(self, tool_name: str = "工具窗口", site_key: str = "", parent=None):
        super().__init__(parent)
        self.tool_name = tool_name
        self.site_key = site_key

        profile = get_site_profile(self.site_key)
        menu_titles = [i.get("title", "") for i in profile["menu_items"] if i.get("visible", True)]

        # 创建组件（左侧菜单 + 右侧内容）
        self.left_panel = LeftMenuPanel(menu_titles)
        self.right_panel = RightContentPanel(tool_name=self.tool_name, site_key=self.site_key)

        # 连接信号
        self.left_panel.menu_item_clicked.connect(self._on_menu_item_clicked)

        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle(f"{self.tool_name}（模块化版）")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 根布局
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 添加左右面板
        root_layout.addWidget(self.left_panel)
        root_layout.addWidget(self.right_panel)

    def _on_menu_item_clicked(self, index: int):
        """菜单项点击处理"""
        menu_item = self.left_panel.get_current_menu_item()
        if menu_item:
            self.right_panel.show_content(menu_item)

    def closeEvent(self, event):
        """窗口关闭事件"""
        super().closeEvent(event)


# 创建别名供导入使用
BaseToolWindow = CheckboxTestWindow


def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = CheckboxTestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
