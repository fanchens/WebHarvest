"""
右侧内容面板组件
管理右侧内容的显示和切换，支持不同类型的页面内容
"""

from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
)

from .component.data_table_widget import DataTableWidget
from .browser_login_page import BrowserLoginPage


class RightContentPanel(QWidget):
    """右侧内容面板组件"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置白色背景
        self.setStyleSheet("QWidget { background-color: #ffffff; }")

        # 创建布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(20)

        # 当前显示的组件
        self.current_content: Optional[QWidget] = None

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

    def _create_content(self, content_type: str) -> Optional[QWidget]:
        """创建指定类型的内容

        注意：这里的键必须和 LeftMenuPanel.DEFAULT_MENU_ITEMS 中的文本完全一致，
        否则会因为匹配不到而回退到默认的“欢迎使用”页面。
        """
        content_map = {
            "作品列表": self._create_works_list,
            "主页提取": self._create_homepage_extraction,
            "单作品提取": self._create_single_work_extraction,
            "关键词提取": self._create_keyword_extraction,
            "我的主页提取": self._create_my_homepage_extraction,
            "万能浏览提取": self._create_universal_browse_extraction,
            "下载设置": self._create_download_settings,
            "VIP中心": self._create_vip_center,
            # 与左侧菜单文本保持一致：浏览器_登录
            "浏览器_登录": self._create_browser_login_page,
            "软件设置": self._create_software_settings,
            "推送消息": self._create_push_messages,
            "语音转写文案": self._create_voice_transcription,
            "使用教程": self._create_tutorial,
        }

        creator = content_map.get(content_type, self._create_default_content)
        return creator()

    def _create_works_list(self) -> QWidget:
        """创建作品列表内容"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建表格
        table = DataTableWidget()
        layout.addWidget(table)

        return container

    def _create_homepage_extraction(self) -> QWidget:
        """创建主页提取内容"""
        return self._create_text_content("主页提取功能", "这里可以配置主页内容的提取设置")

    def _create_single_work_extraction(self) -> QWidget:
        """创建单作品提取内容"""
        return self._create_text_content("单作品提取功能", "输入作品ID或URL进行单个作品提取")

    def _create_keyword_extraction(self) -> QWidget:
        """创建关键词提取内容"""
        return self._create_text_content("关键词提取功能", "输入关键词进行内容搜索和提取")

    def _create_my_homepage_extraction(self) -> QWidget:
        """创建我的主页提取内容"""
        return self._create_text_content("我的主页提取功能", "提取当前登录用户的主页内容")

    def _create_universal_browse_extraction(self) -> QWidget:
        """创建万能浏览提取内容"""
        return self._create_text_content("万能浏览提取功能", "支持多种网站的内容自动提取")

    def _create_download_settings(self) -> QWidget:
        """创建下载设置内容"""
        return self._create_text_content("下载设置", "配置下载路径、并发数、速度限制等")

    def _create_vip_center(self) -> QWidget:
        """创建VIP中心内容"""
        return self._create_text_content("VIP中心", "会员特权、付费功能、升级服务")

    def _create_browser_login_page(self) -> QWidget:
        """创建浏览器登录页面"""
        return BrowserLoginPage()

    def _create_software_settings(self) -> QWidget:
        """创建软件设置内容"""
        return self._create_text_content("软件设置", "界面主题、语言、快捷键等系统配置")

    def _create_push_messages(self) -> QWidget:
        """创建推送消息内容"""
        return self._create_text_content("推送消息", "配置消息推送渠道和通知设置")

    def _create_voice_transcription(self) -> QWidget:
        """创建语音转写内容"""
        return self._create_text_content("语音转写文案", "将语音转换为文字内容")

    def _create_tutorial(self) -> QWidget:
        """创建使用教程内容"""
        return self._create_text_content("使用教程", "查看详细的使用指南和帮助文档")

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

    def get_current_content_type(self) -> Optional[str]:
        """获取当前显示的内容类型"""
        # 这里可以根据当前显示的内容返回相应的类型
        # 暂时返回None，具体实现可以根据需要添加
        return None
