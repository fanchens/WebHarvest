"""
右侧内容面板组件
管理右侧内容的显示和切换，支持不同类型的页面内容
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
)

from .site_profiles import get_site_profile


class RightContentPanel(QWidget):
    """右侧内容面板组件"""

    def __init__(self, parent=None, *, tool_name: str = "", site_key: str = ""):
        super().__init__(parent)
        self._tool_name = tool_name
        self._site_key = site_key

        # 设置白色背景
        self.setStyleSheet("QWidget { background-color: #ffffff; }")

        # 创建布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(20)

        # 当前显示的组件
        self.current_content: QWidget | None = None

        # 初始化显示默认内容
        self.show_default_content()

    def show_default_content(self):
        """显示默认内容（作品列表）"""
        self.show_content("作品列表")

    def show_content(self, content_type: str):
        """根据内容类型显示对应内容"""
        # 清除当前内容
        self._clear_content()

        # 创建新内容
        content = self._create_content(content_type)
        if content:
            self.layout.addWidget(content)
            self.current_content = content

    def _clear_content(self):
        """清除当前显示的内容"""
        if self.current_content:
            self.current_content.hide()
            self.current_content.setParent(None)
            self.current_content.deleteLater()
            self.current_content = None

    def _create_content(self, content_type: str) -> QWidget | None:
        """创建指定类型的内容

        注意：这里的键必须和 LeftMenuPanel.DEFAULT_MENU_ITEMS 中的文本完全一致，
        否则会因为匹配不到而回退到默认的“欢迎使用”页面。
        """
        profile = get_site_profile(self._infer_site_key())
        # 用 title 找到该菜单对应的 page_type
        page_type = None
        for item in profile["menu_items"]:
            if item.get("title") == content_type:
                page_type = item.get("page_type")
                break
        if not page_type:
            return self._create_default_content()

        factory = profile["page_factories"].get(page_type)
        if not factory:
            return self._create_default_content()

        return factory(parent=self, tool_name=self._tool_name, site_key=self._infer_site_key())

    def _infer_site_key(self) -> str:
        """返回站点 key（优先使用配置传入的 site_key，避免依赖中文名称判断）"""
        if self._site_key:
            return self._site_key
        # 兼容：历史路径未传 site_key 时，才回退到从名字推断
        t = (self._tool_name or "").lower()
        if "douyin" in t:
            return "douyin"
        if "xiaohongshu" in t or "xhs" in t:
            return "xiaohongshu"
        if "kuaishou" in t:
            return "kuaishou"
        if "tk" in t or "tiktok" in t:
            return "tiktok"
        if "bili" in t:
            return "bilibili"
        if "youtube" in t:
            return "youtube"
        return "default"

    # 旧的“每个菜单一个 _create_xxx”已迁移到 pages/ 目录，由 site_profiles.py 统一管理。

    def _create_text_content(self, title: str, description: str) -> QWidget:
        """创建文本内容（通用方法）"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)

        # 描述
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                line-height: 1.5;
            }
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # 添加弹性空间
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        return container

    def _create_default_content(self) -> QWidget:
        """创建默认内容"""
        return self._create_text_content("欢迎使用", "请选择左侧菜单项查看相应功能")

    def set_height_mode(self, mode: str, **params):
        """设置高度模式"""
        if mode == "fixed":
            self.setFixedHeight(params.get("height", 600))
        elif mode == "minimum":
            self.setMinimumHeight(params.get("min_height", 400))
        elif mode == "maximum":
            self.setMaximumHeight(params.get("max_height", 800))
        elif mode == "range":
            self.setMinimumHeight(params.get("min_height", 400))
            self.setMaximumHeight(params.get("max_height", 800))
        else:  # auto
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

    def get_current_content_type(self) -> str | None:
        """获取当前显示的内容类型"""
        # 这里可以根据当前显示的内容返回相应的类型
        # 暂时返回None，具体实现可以根据需要添加
        return None
