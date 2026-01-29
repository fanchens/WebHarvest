"""
工具窗口主框架 - 模块化版本（支持 site_key / 动态菜单）
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
from .site_profiles import get_site_profile

# ===================== 窗口配置常量 ======================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800


class CheckboxTestWindow(QMainWindow):
    """工具窗口 - 使用模块化组件"""

    def __init__(self, tool_name: str = "工具窗口", parent=None, *, site_key: str = ""):
        """
        :param tool_name: 工具名称（用于窗口标题、站点推断）
        :param parent: 父窗口
        :param site_key: 站点 key（如 douyin / kuaishou / xiaohongshu 等）
                         - 传入时优先使用
                         - 不传时会根据 tool_name 英文关键字自动推断
        """
        super().__init__(parent)
        self.tool_name = tool_name
        self._site_key = site_key or self._infer_site_key_from_name(tool_name)

        # 根据站点配置生成左侧菜单
        profile = get_site_profile(self._site_key)
        menu_items = [
            item.get("title", "")
            for item in profile.get("menu_items", [])
            if item.get("visible", True)
        ]

        # 创建组件
        self.left_panel = LeftMenuPanel(menu_items=menu_items)
        self.right_panel = RightContentPanel(
            parent=self, tool_name=self.tool_name, site_key=self._site_key
        )

        # 连接信号
        self.left_panel.menu_item_clicked.connect(self._on_menu_item_clicked)

        self.setup_ui()

    def _infer_site_key_from_name(self, name: str) -> str:
        """从工具名称里推断站点 key（兜底逻辑）"""
        t = (name or "").lower()
        if "douyin" in t or "抖音" in t or "dy" in t:
            return "douyin"
        if "kuaishou" in t or "快手" in t or "ks" in t:
            return "kuaishou"
        if "xiaohongshu" in t or "小红书" in t or "xhs" in t:
            return "xiaohongshu"
        if "tk" in t or "tiktok" in t:
            return "tiktok"
        if "bili" in t or "哔哩" in t:
            return "bilibili"
        if "youtube" in t:
            return "youtube"
        return "default"

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
