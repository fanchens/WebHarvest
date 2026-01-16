"""
工具卡片组件
"""

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QFrame,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)

from webharvest.ui.main_window.config.styles_config import (
    TOOL_CARD_STYLE,
    TOOL_CARD_HEADER_STYLE,
    TOOL_CARD_STAR_STYLE,
    TOOL_CARD_NAME_STYLE,
    TOOL_CARD_BUTTON_STYLE,
    TOOL_CARD_DESC_STYLE,
    TOOL_CARD_DESC_TEXT_STYLE,
)


class ToolCard(QFrame):
    """工具卡片 - 支持2列布局的自动宽度计算"""
    
    def __init__(self, name: str, description: str, parent=None):
        super().__init__(parent)
        self._name = name
        self._description = description
        self._star_label = None  # 保存五角星标签引用
        self._is_favorite = False  # 收藏状态
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        self.setFixedHeight(150)  # 固定高度150px
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(TOOL_CARD_STYLE)
        card_layout = QVBoxLayout(self)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # 顶部淡紫色/蓝紫色区域
        header = QWidget()
        header.setFixedHeight(40)  # 设置固定高度40px
        header.setStyleSheet(TOOL_CARD_HEADER_STYLE)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        header.setLayout(header_layout)

        # 星标（可点击收藏）
        self._star_label = QLabel("☆")  # 默认未收藏显示空心星
        self._star_label.setStyleSheet(TOOL_CARD_STAR_STYLE)
        # 添加点击事件
        def make_star_click_handler():
            def handler(event):
                QLabel.mousePressEvent(self._star_label, event)
                self._toggle_favorite()
            return handler
        self._star_label.mousePressEvent = make_star_click_handler()
        # 检查初始收藏状态
        self._update_star_display()
        header_layout.addWidget(self._star_label)

        # 工具名称（居中）
        name_label = QLabel(self._name)
        name_label.setStyleSheet(TOOL_CARD_NAME_STYLE)
        name_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(name_label, stretch=1)

        # 打开软件按钮（右对齐）
        open_btn = QPushButton("打开软件")
        open_btn.setStyleSheet(TOOL_CARD_BUTTON_STYLE)
        open_btn.clicked.connect(lambda: self._on_open_tool())
        header_layout.addWidget(open_btn)

        card_layout.addWidget(header)

        # 底部灰色区域（描述）
        desc_widget = QWidget()
        desc_widget.setStyleSheet(TOOL_CARD_DESC_STYLE)
        desc_layout = QVBoxLayout()
        desc_layout.setContentsMargins(0, 0, 0, 0)
        desc_widget.setLayout(desc_layout)

        desc_label = QLabel(self._description)
        desc_label.setStyleSheet(TOOL_CARD_DESC_TEXT_STYLE)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_layout.addWidget(desc_label)

        card_layout.addWidget(desc_widget)
    
    def _toggle_favorite(self):
        """切换收藏状态"""
        # 动态导入MainWindow，避免循环导入
        main_window = self.window()
        from webharvest.ui.main_window import MainWindow
        if not isinstance(main_window, MainWindow):
            return
        
        if self._name in main_window.favorite_tools:
            # 取消收藏
            main_window.favorite_tools.discard(self._name)
            self._is_favorite = False
        else:
            # 添加收藏
            main_window.favorite_tools.add(self._name)
            self._is_favorite = True
        
        # 更新五角星显示
        self._update_star_display()
        
        # 如果当前显示的是"我的收藏工具"，更新内容
        if hasattr(main_window, 'current_nav_index') and main_window.nav_labels:
            if main_window.current_nav_index < len(main_window.nav_labels):
                current_category = main_window.nav_labels[main_window.current_nav_index].text()
                if current_category == "我的收藏工具":
                    main_window._update_right_content("我的收藏工具")
    
    def _update_star_display(self):
        """更新五角星显示（根据收藏状态）"""
        # 动态导入MainWindow，避免循环导入
        main_window = self.window()
        from webharvest.ui.main_window import MainWindow
        if isinstance(main_window, MainWindow) and self._name in main_window.favorite_tools:
            self._is_favorite = True
        else:
            self._is_favorite = False
        self._star_label.setText("★" if self._is_favorite else "☆")
    
    def _on_open_tool(self):
        """打开工具按钮点击事件"""
        # TODO: 后续实现工具打开逻辑
        print(f"打开工具: {self._name}")
    
    def sizeHint(self):
        """计算建议大小（根据父容器宽度计算，支持2列布局）"""
        parent = self.parent()
        if parent:
            parent_width = parent.width()
            if parent_width > 0:
                available_width = parent_width - 10
                card_width = (available_width - 5) // 2
                return QSize(card_width, 150)
        return QSize(400, 150)

