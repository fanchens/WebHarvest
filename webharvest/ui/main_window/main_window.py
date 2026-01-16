"""
主窗口：WebHarvest 采集工具

布局设计：
- 左侧：上下两部分（导航菜单 + 用户账户信息）
- 右侧：工具卡片网格
"""

from __future__ import annotations
from datetime import datetime

from PySide6.QtCore import Qt, QEvent
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QSplitter,
    QFrame,
    QSizePolicy,
    QScrollArea,
)

# 导入布局类
from webharvest.ui.layouts import FlexLayout, FlowLayout

# 导入组件
from webharvest.ui.widgets.tool_card import ToolCard

# 导入配置
from webharvest.ui.main_window.config.tools_config import get_tools_by_category
from webharvest.ui.main_window.config.navigation_config import NAV_ITEMS, get_visible_nav_items
from webharvest.ui.main_window.config.styles_config import (
    MAIN_WINDOW_STYLE,
    NAV_ITEM_NORMAL_STYLE,
    NAV_ITEM_SELECTED_STYLE,
    USER_PANEL_STYLE,
    BANNER_STYLE,
    BANNER_RED_SECTION_STYLE,
    BANNER_PURPLE_SECTION_STYLE,
    BANNER_BLUE_SECTION_STYLE,
    BANNER_GREEN_SECTION_STYLE,
    BANNER_TEXT_STYLE,
    BANNER_TEXT_SMALL_STYLE,
    BANNER_TEXT_TINY_STYLE,
    DISCLAIMER_CARD_STYLE,
    DISCLAIMER_TITLE_STYLE,
    DISCLAIMER_SECTION_TITLE_STYLE,
    DISCLAIMER_TEXT_STYLE,
    DISCLAIMER_CONTACT_STYLE,
)
from webharvest.ui.main_window.config.content_config import DISCLAIMER_CONTENT, BANNER_CONTENT
from webharvest.ui.main_window.config.app_config import (
    WINDOW_CONFIG,
    SPLITTER_CONFIG,
    USER_DEFAULT_INFO,
    LAYOUT_CONFIG,
    OTHER_CONFIG,
)

# 导入工具函数
from webharvest.utils.widget_utils import ensure_widget_valid, safe_delete_widget, clear_layout


class AutoFillListWidget(QListWidget):
    """自动填充列表控件 - 列表项自动拉伸填充整个控件高度"""
    
    def resizeEvent(self, event):
        """重写resizeEvent，动态调整列表项高度"""
        super().resizeEvent(event)
        self._adjust_item_heights()
    
    def showEvent(self, event):
        """重写showEvent，初始显示时调整列表项高度"""
        super().showEvent(event)
        # 使用定时器延迟执行，确保窗口完全显示后再调整
        from PySide6.QtCore import QTimer
        QTimer.singleShot(10, self._adjust_item_heights)
    
    def _adjust_item_heights(self):
        """动态调整列表项的高度，使其填充整个列表控件"""
        if not self.isVisible() or self.count() == 0:
            return
        
        try:
            # 获取列表控件的可用高度
            list_height = self.viewport().height()
            item_count = self.count()
            
            if list_height > 0 and item_count > 0:
                # 计算每个列表项应该的高度（平均分配）
                item_height = max(list_height // item_count, 30)  # 最小高度30px
                
                # 设置每个列表项的高度
                for i in range(item_count):
                    item = self.item(i)
                    if item:
                        item.setSizeHint(item.sizeHint().width() or 200, item_height)
        except Exception:
            pass  # 忽略错误，避免影响程序运行


class MainWindow(QMainWindow):
    """WebHarvest 主窗口 - 左侧上下两部分布局"""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(WINDOW_CONFIG["title"])
        self.setGeometry(
            WINDOW_CONFIG["x"],
            WINDOW_CONFIG["y"],
            WINDOW_CONFIG["width"],
            WINDOW_CONFIG["height"]
        )

        # 初始化收藏工具集合
        self.favorite_tools = set()  # 存储收藏的工具名称
        
        # 标记当前是否正在显示免责声明
        self._is_showing_disclaimer = False

        # 设置深蓝/紫色主题样式
        self._setup_style()
        self._setup_ui()

    def _setup_style(self) -> None:
        """设置整体样式（深蓝/紫色主题）"""
        self.setStyleSheet(MAIN_WINDOW_STYLE)

    def _setup_ui(self) -> None:
        """搭建主界面结构 - 使用FlexLayout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局（水平Flex）
        main_layout = FlexLayout.create(Qt.Horizontal, spacing=0, margins=(0, 0, 0, 0))
        central_widget.setLayout(main_layout)

        # 主分割器
        main_splitter = QSplitter(Qt.Horizontal)
        FlexLayout.add_flex_widget(main_layout, main_splitter, stretch=1)

        # ========== 左侧区域包装容器（包含左侧内容和红色竖线）==========
        left_wrapper = QWidget()
        left_wrapper_layout = FlexLayout.create(Qt.Horizontal, spacing=0, margins=(0, 0, 0, 0))
        left_wrapper.setLayout(left_wrapper_layout)

        # 左侧内容区域（垂直Flex：上 | 分隔线 | 下）
        left_container = QWidget()
        left_container.setStyleSheet("background-color: #f5f5f5;")
        left_layout = FlexLayout.create(Qt.Vertical, spacing=0, margins=(0, 0, 0, 0))
        left_container.setLayout(left_layout)

        # 左上：导航菜单（弹性拉伸，占满剩余空间）
        top_left_widget = self._create_top_left_panel()
        FlexLayout.add_flex_widget(left_layout, top_left_widget, stretch=1)

        # 红色分隔线（无拉伸）
        separator_line = QFrame()
        separator_line.setFixedHeight(1)
        separator_line.setStyleSheet("background-color: #ff0000; margin: 0px; padding: 0px;")
        FlexLayout.add_flex_widget(left_layout, separator_line, stretch=0)

        # 左下：用户账户信息（无拉伸）
        bottom_left_widget = self._create_bottom_left_panel()
        FlexLayout.add_flex_widget(left_layout, bottom_left_widget, stretch=0)

        FlexLayout.add_flex_widget(left_wrapper_layout, left_container, stretch=1)

        # 红色竖线（无拉伸）
        vertical_red_line = QFrame()
        vertical_red_line.setFixedWidth(2)
        vertical_red_line.setStyleSheet("background-color: #ff0000; margin: 0px; padding: 0px;")
        FlexLayout.add_flex_widget(left_wrapper_layout, vertical_red_line, stretch=0)

        main_splitter.addWidget(left_wrapper)

        # ========== 右侧区域 ==========
        right_widget = self._create_right_panel()
        main_splitter.addWidget(right_widget)

        # 设置主分割器比例
        main_splitter.setSizes(SPLITTER_CONFIG["sizes"])

    def _create_top_left_panel(self) -> QWidget:
        """创建左上区域：导航菜单 - 使用FlexLayout实现均匀分布"""
        widget = QWidget()
        widget.setStyleSheet("background-color: #f5f5f5; margin: 0px; padding: 0px;")
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 导航面板垂直Flex，无边距
        layout = FlexLayout.create(Qt.Vertical, spacing=0, margins=(0, 0, 0, 0))
        widget.setLayout(layout)

        # 导航项容器：垂直Flex，均匀拉伸，无间距
        nav_container = QWidget()
        nav_layout = FlexLayout.create(Qt.Vertical, spacing=0, margins=(0, 0, 0, 0))
        nav_container.setLayout(nav_layout)

        nav_items = get_visible_nav_items()  # 只显示启用的导航项

        # 保存导航项引用，用于点击事件
        self.nav_labels = []
        self.current_nav_index = 0

        # 为每个导航项创建QLabel（替代QListWidgetItem，支持Flex拉伸）
        for idx, item_text in enumerate(nav_items):
            nav_label = QLabel(item_text)
            nav_label.setAlignment(Qt.AlignCenter)
            nav_label.setStyleSheet(NAV_ITEM_NORMAL_STYLE)
            # 每个导航项都设置弹性拉伸（flex:1），均匀占满高度
            FlexLayout.add_flex_widget(nav_layout, nav_label, stretch=1)
            
            # 添加点击事件（使用闭包正确捕获索引）
            def make_click_handler(index):
                def handler(event):
                    # 调用父类方法以保持默认行为
                    QLabel.mousePressEvent(nav_label, event)
                    # 处理点击事件
                    self._on_nav_label_clicked(index)
                return handler
            nav_label.mousePressEvent = make_click_handler(idx)
            # 启用鼠标跟踪以便hover效果正常工作
            nav_label.setMouseTracking(True)
            self.nav_labels.append(nav_label)
            
            # 默认选中第一个
            if idx == 0:
                nav_label.setStyleSheet(NAV_ITEM_SELECTED_STYLE)

        # 导航容器整体拉伸
        FlexLayout.add_flex_widget(layout, nav_container, stretch=1)

        return widget

    def _create_bottom_left_panel(self) -> QWidget:
        """创建左下区域：用户账户信息 - 使用FlexLayout"""
        widget = QWidget()
        widget.setStyleSheet(USER_PANEL_STYLE)
        layout = FlexLayout.create(Qt.Vertical, spacing=3, margins=(12, 0, 12, 8))
        widget.setLayout(layout)

        widget.setStyleSheet(USER_PANEL_STYLE)
        
        # 用户账户信息（无拉伸）
        self.account_label = QLabel(f"软件账户: {USER_DEFAULT_INFO['account']}")
        self.account_label.setObjectName("user_info_label")
        FlexLayout.add_flex_widget(layout, self.account_label, stretch=0)

        self.points_label = QLabel(f"江湖积分: {USER_DEFAULT_INFO['points']}")
        self.points_label.setObjectName("user_info_label")
        FlexLayout.add_flex_widget(layout, self.points_label, stretch=0)

        self.status_label = QLabel(f"江湖地位: {USER_DEFAULT_INFO['status']}")
        self.status_label.setObjectName("user_info_label")
        FlexLayout.add_flex_widget(layout, self.status_label, stretch=0)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.login_label = QLabel(f"上次登录: {current_time}")
        self.login_label.setObjectName("user_info_label")
        FlexLayout.add_flex_widget(layout, self.login_label, stretch=0)

        self.invite_count_label = QLabel(f"邀请数量: {USER_DEFAULT_INFO['invite_count']}")
        self.invite_count_label.setObjectName("user_info_label")
        FlexLayout.add_flex_widget(layout, self.invite_count_label, stretch=0)

        self.invite_code_label = QLabel(f"邀请码: {USER_DEFAULT_INFO['invite_code']}")
        self.invite_code_label.setObjectName("user_info_label")
        FlexLayout.add_flex_widget(layout, self.invite_code_label, stretch=0)

        return widget

    def _create_right_panel(self) -> QWidget:
        """创建右侧区域：工具卡片网格"""
        widget = QWidget()
        widget.setStyleSheet("background-color: #1a1a2e;")  # 深蓝背景
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        widget.setLayout(main_layout)

        # 滚动区域（保存为实例变量，以便后续更新）
        self.right_scroll_area = QScrollArea()
        self.right_scroll_area.setWidgetResizable(True)
        self.right_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.right_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.right_scroll_area.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.right_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1a1a2e;
            }
            QScrollBar:vertical {
                background-color: #16213e;
                width: 10px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #533483;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #6b4c93;
            }
        """)

        # 内容容器（保存为实例变量，以便后续更新）
        # 使用FlowLayout实现类似Flex的自动换行布局
        self.right_content_widget = QWidget()
        self.right_content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        # 使用FlowLayout：自动换行，间距5px，边距5px，左上对齐
        self.right_content_layout = FlowLayout(spacing=5, margin=5)
        self.right_content_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.right_content_widget.setLayout(self.right_content_layout)

        # 初始显示"热门工具"的内容
        self._update_right_content("热门工具")

        self.right_scroll_area.setWidget(self.right_content_widget)
        FlexLayout.add_flex_widget(main_layout, self.right_scroll_area, stretch=1)  # 滚动区域占据剩余空间

        # 底部横幅区域
        banner_widget = self._create_bottom_banner()
        FlexLayout.add_flex_widget(main_layout, banner_widget, stretch=0)  # 横幅固定高度

        return widget

    def _create_bottom_banner(self) -> QWidget:
        """创建底部横幅区域"""
        banner = QWidget()
        banner.setFixedHeight(LAYOUT_CONFIG['banner_height'])  # 固定高度
        banner.setStyleSheet(BANNER_STYLE)
        
        # 水平布局，4个部分平均分配
        banner_layout = FlexLayout.create(Qt.Horizontal, spacing=0, margins=(0, 0, 0, 0))
        banner.setLayout(banner_layout)
        
        # 1. 红色区域：微信客服
        red_section = QWidget()
        red_section.setStyleSheet(f"background-color: {BANNER_CONTENT['wechat']['color']}; cursor: pointer;")
        red_layout = QHBoxLayout()
        red_layout.setContentsMargins(10, 0, 10, 0)
        red_layout.setSpacing(8)
        red_section.setLayout(red_layout)
        
        # 微信图标（使用文字符号代替，实际可以用图片）
        wechat_icon = QLabel(BANNER_CONTENT['wechat']['icon'])
        wechat_icon.setStyleSheet("color: #ffffff; font-size: 24px; border: none; background-color: transparent;")
        wechat_icon.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # 让标签不拦截鼠标事件
        red_layout.addWidget(wechat_icon)
        
        wechat_text = QLabel(BANNER_CONTENT['wechat']['text'])
        wechat_text.setStyleSheet(BANNER_TEXT_STYLE)
        wechat_text.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # 让标签不拦截鼠标事件
        red_layout.addWidget(wechat_text)
        # 添加点击事件
        def wechat_click(event):
            QWidget.mousePressEvent(red_section, event)
            self._on_wechat_click()
        red_section.mousePressEvent = wechat_click
        FlexLayout.add_flex_widget(banner_layout, red_section, stretch=1)
        
        # 2. 紫色区域：官网地址
        purple_section = QWidget()
        purple_section.setStyleSheet(f"background-color: {BANNER_CONTENT['website']['color']}; cursor: pointer;")
        purple_layout = QVBoxLayout()
        purple_layout.setContentsMargins(10, 5, 10, 5)
        purple_layout.setSpacing(2)
        purple_section.setLayout(purple_layout)
        
        website_text1 = QLabel(BANNER_CONTENT['website']['text1'])
        website_text1.setStyleSheet(BANNER_TEXT_SMALL_STYLE)
        website_text1.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # 让标签不拦截鼠标事件
        purple_layout.addWidget(website_text1)
        
        website_text2 = QLabel(BANNER_CONTENT['website']['text2'])
        website_text2.setStyleSheet(BANNER_TEXT_TINY_STYLE)
        website_text2.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # 让标签不拦截鼠标事件
        purple_layout.addWidget(website_text2)
        # 添加点击事件
        def website_click(event):
            QWidget.mousePressEvent(purple_section, event)
            self._on_website_click()
        purple_section.mousePressEvent = website_click
        FlexLayout.add_flex_widget(banner_layout, purple_section, stretch=1)
        
        # 3. 蓝色区域：打赏
        blue_section = QWidget()
        blue_section.setStyleSheet(f"background-color: {BANNER_CONTENT['tip']['color']}; cursor: pointer;")
        blue_layout = QVBoxLayout()
        blue_layout.setContentsMargins(10, 0, 10, 0)
        blue_section.setLayout(blue_layout)
        
        tip_text = QLabel(BANNER_CONTENT['tip']['text'])
        tip_text.setAlignment(Qt.AlignCenter)
        tip_text.setStyleSheet(BANNER_TEXT_STYLE)
        tip_text.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # 让标签不拦截鼠标事件
        blue_layout.addWidget(tip_text)
        # 添加点击事件
        def tip_click(event):
            QWidget.mousePressEvent(blue_section, event)
            self._on_tip_click()
        blue_section.mousePressEvent = tip_click
        FlexLayout.add_flex_widget(banner_layout, blue_section, stretch=1)
        
        # 4. 绿色区域：免责声明
        green_section = QWidget()
        green_section.setStyleSheet(f"background-color: {BANNER_CONTENT['disclaimer']['color']}; cursor: pointer;")
        green_layout = QVBoxLayout()
        green_layout.setContentsMargins(10, 5, 10, 5)
        green_layout.setSpacing(2)
        green_section.setLayout(green_layout)
        
        disclaimer_text1 = QLabel(BANNER_CONTENT['disclaimer']['text1'])
        disclaimer_text1.setStyleSheet(BANNER_TEXT_SMALL_STYLE)
        disclaimer_text1.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # 让标签不拦截鼠标事件
        green_layout.addWidget(disclaimer_text1)
        
        disclaimer_text2 = QLabel(BANNER_CONTENT['disclaimer']['text2'])
        disclaimer_text2.setStyleSheet(BANNER_TEXT_TINY_STYLE)
        disclaimer_text2.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # 让标签不拦截鼠标事件
        green_layout.addWidget(disclaimer_text2)
        # 添加点击事件到整个区域
        def disclaimer_click(event):
            QWidget.mousePressEvent(green_section, event)
            self._on_disclaimer_click()
        green_section.mousePressEvent = disclaimer_click
        FlexLayout.add_flex_widget(banner_layout, green_section, stretch=1)
        
        return banner

    def _get_tools_by_category(self, category: str) -> list:
        """根据分类获取对应的工具列表"""
        return get_tools_by_category(category, self.favorite_tools)

    def _update_right_content(self, category: str) -> None:
        """更新右侧内容区域，根据选中的分类显示对应的工具"""
        print(f"更新右侧内容: {category}")
        
        # 如果正在显示免责声明，不更新内容（防止意外替换免责声明widget）
        # 只有在用户点击导航项时，才允许从免责声明切换回工具列表
        if self._is_showing_disclaimer:
            # 检查当前widget是否真的是免责声明widget
            current_widget = self.right_scroll_area.widget() if hasattr(self, 'right_scroll_area') else None
            # 如果标志为True，无论当前widget是什么，都不更新（防止在设置widget过程中被替换）
            print("正在显示免责声明，跳过内容更新")
            return
        
        # 检查 scroll_area 是否存在
        if not hasattr(self, 'right_scroll_area'):
            print(f"错误: right_scroll_area 未初始化")
            return
        
        # 检查 right_content_widget 是否存在且有效
        if not hasattr(self, 'right_content_widget') or self.right_content_widget is None:
            # 重新创建 right_content_widget
            print("重新创建 right_content_widget")
            self.right_content_widget = QWidget()
            self.right_content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.right_content_layout = FlowLayout(spacing=5, margin=5)
            self.right_content_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.right_content_widget.setLayout(self.right_content_layout)
        else:
            # 检查 right_content_widget 是否仍然有效（没有被删除）
            try:
                # 尝试访问widget的属性来检查是否有效
                _ = self.right_content_widget.sizePolicy()
            except RuntimeError:
                # 如果已经被删除，重新创建
                print("right_content_widget 已被删除，重新创建")
                self.right_content_widget = QWidget()
                self.right_content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
                self.right_content_layout = FlowLayout(spacing=5, margin=5)
                self.right_content_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
                self.right_content_widget.setLayout(self.right_content_layout)
        
        # 确保 scroll_area 显示的是 right_content_widget（而不是免责声明widget）
        current_widget = self.right_scroll_area.widget()
        if current_widget != self.right_content_widget:
            # 如果当前显示的是免责声明widget，不应该执行到这里（因为前面已经检查并返回了）
            # 但为了安全，再次检查并清除标志
            if self._is_showing_disclaimer:
                print("警告: 在更新内容时发现免责声明标志仍为True，清除标志")
                self._is_showing_disclaimer = False
            # 只有在不是免责声明widget时才替换
            self.right_scroll_area.setWidget(self.right_content_widget)
        
        # 检查当前布局是否是 FlowLayout，如果不是，需要恢复
        current_layout = self.right_content_widget.layout()
        if not isinstance(current_layout, FlowLayout):
            # 需要恢复 FlowLayout
            if current_layout:
                # 同步清空布局（先同步清空，再异步删除）
                old_widgets = []
                while current_layout.count() > 0:
                    item = current_layout.takeAt(0)
                    if item and item.widget():
                        widget = item.widget()
                        widget.setParent(None)  # 立即断开父子关系
                        old_widgets.append(widget)
                current_layout.setParent(None)
                # 延迟删除旧布局和widget（延长延迟时间，确保新布局创建完成后再删除）
                from PySide6.QtCore import QTimer
                def delete_old():
                    try:
                        if current_layout:
                            current_layout.deleteLater()
                        for w in old_widgets:
                            try:
                                if w:
                                    w.deleteLater()
                            except RuntimeError:
                                pass
                    except Exception as e:
                        print(f"删除旧widget时出错: {e}")
                QTimer.singleShot(500, delete_old)  # 延长到500ms
            
            # 创建新的 FlowLayout（在清空后立即创建，但删除延迟进行）
            self.right_content_layout = FlowLayout(spacing=5, margin=5)
            self.right_content_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.right_content_widget.setLayout(self.right_content_layout)
        else:
            # 使用现有的 FlowLayout，同步清空现有内容
            while self.right_content_layout.count():
                child = self.right_content_layout.takeAt(0)
                if child and child.widget():
                    widget = child.widget()
                    widget.setParent(None)  # 立即断开父子关系
                    widget.deleteLater()  # 异步删除
        
        # 触发布局更新（清空后）
        self.right_content_layout.invalidate()

        # 获取对应分类的工具列表
        tools = self._get_tools_by_category(category)
        print(f"找到 {len(tools)} 个工具")

        # 创建工具卡片（FlowLayout自动处理换行和间距）
        for i, tool in enumerate(tools):
            card = self._create_tool_card(tool["name"], tool["description"])
            # 更新五角星的收藏状态显示
            card._update_star_display()
            # 确保卡片可见
            card.show()
            # FlowLayout会自动处理换行，类似Flex的wrap效果
            self.right_content_layout.addWidget(card)
            print(f"  添加卡片 {i+1}: {tool['name']}")
        
        # 强制更新布局和容器
        self.right_content_layout.invalidate()
        
        # 使用QTimer延迟更新，确保容器已经有正确的大小
        from PySide6.QtCore import QTimer
        def delayed_update():
            # 获取容器的实际大小
            container_rect = self.right_content_widget.geometry()
            if container_rect.width() <= 0:
                # 如果容器还没有大小，尝试从父容器获取
                parent = self.right_content_widget.parent()
                if parent and hasattr(parent, 'viewport'):
                    # 如果是QScrollArea，使用viewport的大小
                    viewport = parent.viewport()
                    if viewport:
                        container_rect = viewport.geometry()
                elif parent:
                    container_rect = parent.geometry()
            
            # 如果还是没有大小，使用sizeHint
            if container_rect.width() <= 0:
                size_hint = self.right_content_widget.sizeHint()
                container_rect = QRect(0, 0, size_hint.width(), size_hint.height())
            
            # 手动触发布局计算
            if container_rect.width() > 0:
                self.right_content_layout.setGeometry(container_rect)
                print(f"  布局已更新，rect: {container_rect.width()}x{container_rect.height()}")
            
            self.right_content_widget.updateGeometry()
            self.right_content_widget.update()
            self.right_content_widget.adjustSize()
        
        # 延迟10ms执行，确保UI已经更新
        QTimer.singleShot(10, delayed_update)
        
        print(f"右侧内容已更新，卡片数量: {self.right_content_layout.count()}")

    def _create_tool_card(self, name: str, description: str) -> ToolCard:
        """创建工具卡片 - 使用ToolCard类"""
        card = ToolCard(name, description, self.right_content_widget)
        return card

    # ========== 事件处理方法（暂时留空） ==========

    def _on_nav_label_clicked(self, index: int) -> None:
        """导航标签点击事件 - FlexLayout版本"""
        # 检查索引有效性
        if not hasattr(self, 'nav_labels') or not self.nav_labels:
            print(f"警告: nav_labels 未初始化")
            return
        
        if not (0 <= index < len(self.nav_labels)):
            print(f"警告: 索引 {index} 超出范围 [0, {len(self.nav_labels)})")
            return
        
        # 如果正在显示免责声明，先清除标志，允许切换到工具列表
        if self._is_showing_disclaimer:
            print("从免责声明切换回工具列表")
            self._is_showing_disclaimer = False
        
        # 更新选中状态
        for i, label in enumerate(self.nav_labels):
            if i == index:
                # 选中状态
                label.setStyleSheet("""
                    QLabel {
                        padding: 8px 12px;
                        background-color: #5a2e8e;
                        color: #ffffff;
                        font-size: 14px;
                        font-weight: bold;
                    }
                """)
            else:
                # 未选中状态
                label.setStyleSheet("""
                    QLabel {
                        padding: 8px 12px;
                        background-color: #f5f5f5;
                        color: #333333;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QLabel:hover {
                        background-color: #e8e8e8;
                    }
                """)
        
        self.current_nav_index = index
        category = self.nav_labels[index].text()
        print(f"导航点击: {category} (索引: {index})")
        self._update_right_content(category)

    def _on_nav_item_changed(self, current, previous) -> None:
        """导航项改变事件（保留兼容性，如果还有QListWidget的话）"""
        if current:
            category = current.text()
            self._update_right_content(category)

    def _on_open_tool(self, tool_name: str) -> None:
        """打开工具按钮点击事件"""
        # TODO: 后续实现工具打开逻辑
        print(f"打开工具: {tool_name}")

    def _on_wechat_click(self) -> None:
        """微信客服点击事件"""
        # TODO: 后续实现打开微信群逻辑
        print("点击微信客服")

    def _on_website_click(self) -> None:
        """官网地址点击事件"""
        import webbrowser
        webbrowser.open(BANNER_CONTENT['website']['url'])

    def _on_tip_click(self) -> None:
        """打赏点击事件"""
        # TODO: 后续实现打赏逻辑
        print("点击打赏")

    def _on_disclaimer_click(self) -> None:
        """免责声明点击事件"""
        self._show_disclaimer_content()

    def _show_disclaimer_content(self) -> None:
        """显示免责声明内容"""
        print("显示免责声明内容")
        # 检查scroll_area是否存在
        if not hasattr(self, 'right_scroll_area'):
            print("错误: right_scroll_area 未初始化")
            return
        
        # 如果已经在显示免责声明，直接返回，避免重复创建
        if self._is_showing_disclaimer:
            current_widget = self.right_scroll_area.widget()
            if current_widget and hasattr(current_widget, 'layout') and current_widget.layout():
                # 已经在显示免责声明，不需要重复创建
                print("免责声明已显示，跳过重复创建")
                return
        
        # 立即设置标志，表示正在显示免责声明（在创建widget之前设置，防止其他事件触发更新）
        self._is_showing_disclaimer = True
        
        # 保存当前的widget（如果有的话），并设置父对象为None，防止被删除
        current_widget = self.right_scroll_area.widget()
        if current_widget and current_widget == getattr(self, 'right_content_widget', None):
            # 如果当前widget是right_content_widget，保存它的引用，并设置父对象为None
            # 这样它就不会被Qt自动删除
            try:
                self.right_content_widget.setParent(None)
            except RuntimeError:
                # 如果已经被删除，重新创建
                self.right_content_widget = None
        
        # 创建新的widget来显示免责声明（不指定父对象，避免被自动删除）
        disclaimer_widget = QWidget()
        disclaimer_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        disclaimer_layout = QVBoxLayout(disclaimer_widget)
        disclaimer_layout.setContentsMargins(0, 0, 0, 0)
        disclaimer_layout.setSpacing(0)

        # 创建免责声明内容卡片（指定父对象为disclaimer_widget）
        disclaimer_card = QFrame(disclaimer_widget)
        disclaimer_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        disclaimer_card.setContentsMargins(0, 0, 0, 0)
        disclaimer_card.setStyleSheet(DISCLAIMER_CARD_STYLE)
        card_layout = QVBoxLayout(disclaimer_card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)

        # 标题（指定父对象为disclaimer_card）
        title_label = QLabel(DISCLAIMER_CONTENT['title'], disclaimer_card)
        title_label.setStyleSheet(DISCLAIMER_TITLE_STYLE)
        title_label.setAlignment(Qt.AlignLeft)
        card_layout.addWidget(title_label)

        # 第一部分：免责声明
        section1_title = QLabel(DISCLAIMER_CONTENT['section1']['title'], disclaimer_card)
        section1_title.setStyleSheet(DISCLAIMER_SECTION_TITLE_STYLE)
        section1_title.setAlignment(Qt.AlignLeft)
        card_layout.addWidget(section1_title)

        content1_label = QLabel(DISCLAIMER_CONTENT['section1']['content'], disclaimer_card)
        content1_label.setStyleSheet(DISCLAIMER_TEXT_STYLE)
        content1_label.setWordWrap(True)
        content1_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        card_layout.addWidget(content1_label)

        # 第二部分：关于如有侵权或占用版权问题声明
        section2_title = QLabel(DISCLAIMER_CONTENT['section2']['title'], disclaimer_card)
        section2_title.setStyleSheet(DISCLAIMER_SECTION_TITLE_STYLE)
        section2_title.setAlignment(Qt.AlignLeft)
        card_layout.addWidget(section2_title)

        content2_label = QLabel(DISCLAIMER_CONTENT['section2']['content'], disclaimer_card)
        content2_label.setStyleSheet(DISCLAIMER_TEXT_STYLE)
        content2_label.setWordWrap(True)
        content2_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        card_layout.addWidget(content2_label)

        # 第三部分：投诉与建议联系邮箱
        section3_text = QLabel(DISCLAIMER_CONTENT['contact_email'], disclaimer_card)
        section3_text.setStyleSheet(DISCLAIMER_CONTACT_STYLE)
        section3_text.setAlignment(Qt.AlignLeft)
        card_layout.addWidget(section3_text)

        # 移除 addStretch()，避免布局计算溢出

        # 添加到布局
        disclaimer_layout.addWidget(disclaimer_card)
        
        # 使用QTimer延迟设置widget，确保标志已经生效，防止其他事件触发更新
        from PySide6.QtCore import QTimer
        def set_disclaimer_widget():
            # 再次检查标志，确保没有被清除
            if not self._is_showing_disclaimer:
                print("警告: 免责声明标志已被清除，取消设置widget")
                return
            disclaimer_widget.show()
            self.right_scroll_area.setWidget(disclaimer_widget)
            print("免责声明内容更新完成")
        
        # 延迟10ms设置widget，确保标志已经生效
        QTimer.singleShot(10, set_disclaimer_widget)
