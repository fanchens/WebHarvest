"""
工具窗口主框架 - 模块化版本
使用独立的组件：左侧菜单面板、右侧内容面板、数据表格组件
"""
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
)

from .left_menu_panel import LeftMenuPanel
from .right_content_panel import RightContentPanel

# ===================== 窗口配置常量 ======================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800


class CheckboxTestWindow(QMainWindow):
    """工具窗口 - 使用模块化组件"""

    def __init__(self, tool_name: str = "工具窗口", parent=None):
        super().__init__(parent)
        self.tool_name = tool_name

        # 创建组件
        self.left_panel = LeftMenuPanel()
        # 把当前“工具名”传给右侧内容面板，用于按站点显示不同内容（如 浏览器_登录 的链接）
        self.right_panel = RightContentPanel(tool_name=self.tool_name)

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






