"""
工具窗口基类
提供统一的工具窗口界面：左侧菜单 + 右侧内容区域
"""

from __future__ import annotations

from functools import partial

from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QCheckBox,
)

# 导入布局工具
from webharvest.ui.layouts import FlexLayout

# 导入配置
from webharvest.ui.tool_windows.config.menu_config import get_tool_menu_config
from webharvest.ui.tool_windows.config.styles_config import (
    TOOL_WINDOW_STYLE,
    TOOL_WINDOW_MENU_CONTAINER_STYLE,
    TOOL_WINDOW_MENU_ITEM_NORMAL_STYLE,
    TOOL_WINDOW_MENU_ITEM_SELECTED_STYLE,
    TOOL_WINDOW_CONTENT_STYLE,
    TOOL_WINDOW_TABLE_STYLE,
)


class BaseToolWindow(QMainWindow):
    """工具窗口基类 - 左侧菜单 + 右侧内容区域"""

    def __init__(self, tool_name: str, parent=None):
        """
        初始化工具窗口
        
        :param tool_name: 工具名称（用于获取菜单配置）
        :param parent: 父窗口
        """
        super().__init__(parent)
        self.tool_name = tool_name
        self.menu_config = get_tool_menu_config(tool_name)
        
        # 当前选中的菜单项索引
        self.current_menu_index = 0
        
        # 菜单项标签列表
        self.menu_labels = []
        
        # 表头全选复选框（初始化为None，在设置表头时创建）
        self.select_all_checkbox = None
        
        # 设置窗口属性
        self._setup_window()
        
        # 设置样式
        self._setup_style()
        
        # 搭建UI
        self._setup_ui()

    def _setup_window(self):
        """设置窗口基本属性"""
        self.setWindowTitle(self.menu_config.get("title", "工具窗口"))
        self.setGeometry(200, 200, 1200, 800)  # x, y, width, height

    def _setup_style(self):
        """设置窗口样式"""
        self.setStyleSheet(TOOL_WINDOW_STYLE)

    def _setup_ui(self):
        """搭建UI结构"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局（水平分割：左侧菜单 + 右侧内容）
        main_layout = FlexLayout.create(Qt.Horizontal, spacing=0, margins=(0, 0, 0, 0))
        central_widget.setLayout(main_layout)
        
        # 左侧菜单
        left_menu_widget = self._create_left_menu()
        FlexLayout.add_flex_widget(main_layout, left_menu_widget, stretch=0)
        
        # 右侧内容区域（暂时留空）
        right_content_widget = self._create_right_content()
        FlexLayout.add_flex_widget(main_layout, right_content_widget, stretch=1)

    def _create_left_menu(self) -> QWidget:
        """创建左侧菜单"""
        menu_widget = QWidget()
        menu_widget.setStyleSheet(TOOL_WINDOW_MENU_CONTAINER_STYLE)
        menu_widget.setFixedWidth(200)  # 固定宽度200px
        
        menu_layout = FlexLayout.create(Qt.Vertical, spacing=0, margins=(0, 0, 0, 0))
        menu_widget.setLayout(menu_layout)
        
        # 获取菜单项配置
        menu_items = self.menu_config.get("menu_items", [])
        
        # 创建菜单项
        for idx, item_config in enumerate(menu_items):
            if not item_config.get("enabled", True):
                continue
            
            item_name = item_config.get("name", "")
            item_icon = item_config.get("icon", None)
            
            # 创建菜单项标签
            menu_label = QLabel()
            
            # 如果有图标，显示图标+文字，否则只显示文字
            if item_icon:
                menu_label.setText(f"{item_icon} {item_name}")
            else:
                menu_label.setText(item_name)
            
            menu_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            # 设置初始样式（第一个默认选中）
            if idx == 0:
                menu_label.setStyleSheet(TOOL_WINDOW_MENU_ITEM_SELECTED_STYLE)
            else:
                menu_label.setStyleSheet(TOOL_WINDOW_MENU_ITEM_NORMAL_STYLE)
            
            # 添加点击事件
            def make_click_handler(index):
                def handler(event):
                    QLabel.mousePressEvent(menu_label, event)
                    self._on_menu_item_clicked(index)
                return handler
            menu_label.mousePressEvent = make_click_handler(idx)
            
            # 启用鼠标跟踪以便hover效果正常工作
            menu_label.setMouseTracking(True)
            
            # 添加到布局（每个菜单项均匀分布）
            FlexLayout.add_flex_widget(menu_layout, menu_label, stretch=1)
            
            self.menu_labels.append(menu_label)
        
        return menu_widget

    def _create_right_content(self) -> QWidget:
        """创建右侧内容区域：表格占据五分之三空间"""
        content_widget = QWidget()
        content_widget.setStyleSheet(TOOL_WINDOW_CONTENT_STYLE)
        
        # 主布局（垂直）
        content_layout = FlexLayout.create(Qt.Vertical, spacing=0, margins=(0, 0, 0, 0))
        content_widget.setLayout(content_layout)
        
        # 表格区域（占据五分之三，即60%）
        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet(TOOL_WINDOW_TABLE_STYLE)
        # 完全禁用所有编辑功能
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止编辑
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)  # 选择整行
        self.table_widget.setAlternatingRowColors(True)  # 交替行颜色
        self.table_widget.horizontalHeader().setStretchLastSection(True)  # 最后一列自动拉伸
        self.table_widget.verticalHeader().setVisible(False)  # 隐藏行号
        self.table_widget.setShowGrid(False)  # 不显示网格线（去除边框）
        self.table_widget.setGridStyle(Qt.NoPen)  # 无网格线
        
        # 注意：不再需要连接 itemChanged 信号，因为改用 QCheckBox 控件
        
        # 表格占据五分之三（stretch=3），其他区域占据五分之二（stretch=2）
        FlexLayout.add_flex_widget(content_layout, self.table_widget, stretch=3)
        
        # 其他内容区域（占据五分之二，暂时留空）
        other_content_widget = QWidget()
        other_content_widget.setStyleSheet(TOOL_WINDOW_CONTENT_STYLE)
        other_layout = QVBoxLayout()
        other_layout.setContentsMargins(20, 20, 20, 20)
        other_content_widget.setLayout(other_layout)
        
        placeholder_label = QLabel("其他功能区域\n（待实现）")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("""
            QLabel {
                color: #999999;
                font-size: 14px;
                background-color: transparent;
            }
        """)
        other_layout.addWidget(placeholder_label)
        
        FlexLayout.add_flex_widget(content_layout, other_content_widget, stretch=2)
        
        # 保存为实例变量
        self.right_content_widget = content_widget
        self.right_content_layout = content_layout
        self.other_content_widget = other_content_widget
        
        # 初始化表格（显示第一个菜单项的内容）
        menu_items = self.menu_config.get("menu_items", [])
        if menu_items:
            first_item_name = menu_items[0].get("name", "")
            self._update_table_content(first_item_name)
        
        return content_widget

    def _on_menu_item_clicked(self, index: int):
        """菜单项点击事件处理"""
        # 检查索引有效性
        if not (0 <= index < len(self.menu_labels)):
            return
        
        # 更新选中状态
        for i, label in enumerate(self.menu_labels):
            if i == index:
                # 选中状态（粉色背景）
                label.setStyleSheet(TOOL_WINDOW_MENU_ITEM_SELECTED_STYLE)
            else:
                # 未选中状态（蓝色背景）
                label.setStyleSheet(TOOL_WINDOW_MENU_ITEM_NORMAL_STYLE)
        
        self.current_menu_index = index
        
        # 获取菜单项名称
        menu_items = self.menu_config.get("menu_items", [])
        if index < len(menu_items):
            item_name = menu_items[index].get("name", "")
            print(f"点击菜单项: {item_name}")
            
            # 更新表格内容
            self._update_table_content(item_name)
    
    def _update_table_content(self, menu_item_name: str):
        """根据菜单项名称更新表格内容"""
        # 清空表格
        self.table_widget.clear()
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)
        # 重置全选复选框
        self.select_all_checkbox = None
        
        # 根据菜单项名称设置不同的表格内容
        if menu_item_name == "作品列表":
            self._setup_works_list_table()
        elif menu_item_name == "主页提取":
            self._setup_homepage_extract_table()
        elif menu_item_name == "单作品提取":
            self._setup_single_work_extract_table()
        elif menu_item_name == "关键词提取":
            self._setup_keyword_extract_table()
        elif menu_item_name == "我的主页提取":
            self._setup_my_homepage_extract_table()
        elif menu_item_name == "万能浏览提取":
            self._setup_universal_browse_extract_table()
        else:
            # 默认表格（其他菜单项）
            self._setup_default_table(menu_item_name)
    
    def _setup_table_header_with_checkbox(self, data_headers: list):
        """设置表格表头，第一列是多选框，第二列是序号，后面是数据列"""
        # 总列数 = 多选框(1) + 序号(1) + 数据列数
        total_columns = 2 + len(data_headers)
        self.table_widget.setColumnCount(total_columns)
        
        # 设置表头标签（先设置所有表头）
        headers = ["选择", "序号"] + data_headers
        self.table_widget.setHorizontalHeaderLabels(headers)
        
        # 设置第一列表头为空（用于放置全选复选框）
        header_item = QTableWidgetItem("")
        header_item.setTextAlignment(Qt.AlignCenter)
        self.table_widget.setHorizontalHeaderItem(0, header_item)
        
        # 设置表头全选复选框（在设置表头之后调用）
        self._setup_checkbox_header()
        
        # 设置列宽
        self.table_widget.setColumnWidth(0, 50)   # 多选框列
        self.table_widget.setColumnWidth(1, 60)   # 序号列
    
    def _setup_checkbox_header(self):
        """设置表头第一列的全选框（用于全选）"""
        # 创建全选复选框（完全按照01.py的方式，无任何样式表）
        self.select_all_checkbox = QCheckBox()
        # 不设置任何样式表，使用Qt完全默认的样式（与test_checkbox.py完全一致）
        # 先连接调试，再连接处理函数，确保调试信息在最后
        def debug_state_change(state):
            print(f"\n=== 表头全选复选框状态改变（调试） ===")
            print(f"state: {state}, Qt.Checked={Qt.Checked}, Qt.Unchecked={Qt.Unchecked}")
            print(f"isChecked: {self.select_all_checkbox.isChecked()}")
            print(f"checkState: {self.select_all_checkbox.checkState()}")
        self.select_all_checkbox.stateChanged.connect(debug_state_change)
        # 最后连接处理函数，确保能获取到正确的状态
        self.select_all_checkbox.stateChanged.connect(self._on_select_all_changed)

        # 在表头绘制完成后设置复选框（使用定时器延迟设置）
        def set_header_checkbox():
            header = self.table_widget.horizontalHeader()
            if header and self.select_all_checkbox:
                # 在表头第一列居中位置添加复选框
                self.select_all_checkbox.setParent(header)
                # 设置复选框大小，确保可以点击（参考01.py，使用默认大小）
                # 不设置固定大小，让Qt使用默认大小
                checkbox_size = self.select_all_checkbox.sizeHint()
                # 使用 sectionViewportPosition 和 sectionSize 获取第一列的位置和大小
                x = header.sectionViewportPosition(0)
                width = header.sectionSize(0)
                height = header.height()
                self.select_all_checkbox.move(
                    x + (width - checkbox_size.width()) // 2,
                    (height - checkbox_size.height()) // 2
                )
                self.select_all_checkbox.show()
                self.select_all_checkbox.raise_()  # 确保在最上层
                self.select_all_checkbox.setEnabled(True)  # 确保启用
                print(f"表头复选框已设置: 位置=({x + (width - checkbox_size.width()) // 2}, {(height - checkbox_size.height()) // 2}), 大小={checkbox_size}")
                # 监听表头大小变化，更新复选框位置
                header.sectionResized.connect(self._update_header_checkbox_position)
                header.sectionMoved.connect(self._update_header_checkbox_position)

        QTimer.singleShot(200, set_header_checkbox)

    def _update_header_checkbox_position(self):
        """更新表头复选框位置（当表头大小或位置改变时）"""
        if self.select_all_checkbox and self.table_widget.horizontalHeader():
            header = self.table_widget.horizontalHeader()
            x = header.sectionViewportPosition(0)
            width = header.sectionSize(0)
            height = header.height()
            self.select_all_checkbox.move(
                x + (width - self.select_all_checkbox.width()) // 2,
                (height - self.select_all_checkbox.height()) // 2
            )

    def _on_select_all_changed(self, state):
        """全选复选框状态改变事件（参考01.py的实现）"""
        # 直接从复选框获取状态，而不是依赖参数（避免信号顺序问题）
        is_checked = self.select_all_checkbox.isChecked()
        print(f"\n=== 执行全选操作 ===")
        print(f"state参数: {state}, Qt.Checked={Qt.Checked}")
        print(f"从复选框获取is_checked: {is_checked}")
        print(f"表格总行数: {self.table_widget.rowCount()}")
        
        # 遍历单元格中的 QCheckBox 控件，并阻止信号避免循环触发
        # 参考01.py：只处理启用的复选框（跳过禁用的）
        updated_count = 0
        for row in range(self.table_widget.rowCount()):
            check_container = self.table_widget.cellWidget(row, 0)
            if check_container:
                checkbox = check_container.findChild(QCheckBox)
                if checkbox:
                    # 关键：用 isEnabled() 判断是否启用（True=启用，False=禁用）
                    # 参考01.py的实现，只处理启用的复选框
                    if checkbox.isEnabled():
                        # 阻止信号，避免触发 _on_cell_checkbox_changed
                        checkbox.blockSignals(True)
                        checkbox.setChecked(is_checked)
                        checkbox.blockSignals(False)
                        updated_count += 1
                        print(f"  更新第 {row + 1} 行复选框: {is_checked}")
                    else:
                        print(f"  跳过第 {row + 1} 行复选框（已禁用）")
            else:
                print(f"  警告：第 {row + 1} 行没有复选框容器")

        print(f"总共更新了 {updated_count} 个复选框")
    
    def _on_cell_checkbox_changed(self, row: int, state: int = None):
        """单元格复选框状态改变事件（更新全选复选框）"""
        # 调试输出
        check_container = self.table_widget.cellWidget(row, 0)
        if check_container:
            checkbox = check_container.findChild(QCheckBox)
            if checkbox:
                print(f"\n=== 复选框状态改变调试 ===")
                print(f"行: {row + 1}")
                print(f"state参数: {state}")
                print(f"isChecked(): {checkbox.isChecked()}")
                print(f"checkState(): {checkbox.checkState()}")
                print(f"Qt.Checked = {Qt.Checked}")
                print(f"Qt.Unchecked = {Qt.Unchecked}")
                
                # 检查样式
                style = checkbox.styleSheet()
                print(f"复选框样式表长度: {len(style) if style else 0}")
                
                # 检查表格样式中的checked部分
                table_style = self.table_widget.styleSheet()
                if "QTableWidget QCheckBox::indicator:checked" in table_style:
                    checked_style_start = table_style.find("QTableWidget QCheckBox::indicator:checked")
                    checked_style_end = table_style.find("}", checked_style_start)
                    if checked_style_end > checked_style_start:
                        checked_style = table_style[checked_style_start:checked_style_end+1]
                        print(f"表格样式中checked部分: {checked_style[:200]}")
                
                status = "选中" if checkbox.isChecked() else "取消选中"
        
        # 使用 QTimer.singleShot(0) 延迟更新，避免在批量设置时频繁触发
        QTimer.singleShot(0, self._update_select_all_checkbox_state)
    
    def _update_select_all_checkbox_state(self):
        """根据当前行的复选框状态更新全选复选框状态（仅两种状态，无半选）
        参考01.py的实现，只统计启用的复选框
        """
        if not self.select_all_checkbox:
            return

        total_rows = self.table_widget.rowCount()
        if total_rows == 0:
            self.select_all_checkbox.blockSignals(True)
            self.select_all_checkbox.setCheckState(Qt.Unchecked)
            self.select_all_checkbox.blockSignals(False)
            return

        # 统计启用的复选框数量和已选中的数量
        enabled_count = 0
        checked_count = 0
        for row in range(total_rows):
            # 获取单元格中的 QCheckBox 控件
            check_container = self.table_widget.cellWidget(row, 0)
            if check_container:
                checkbox = check_container.findChild(QCheckBox)
                if checkbox:
                    # 参考01.py：只统计启用的复选框
                    if checkbox.isEnabled():
                        enabled_count += 1
                        if checkbox.isChecked():
                            checked_count += 1

        # 更新全选复选框状态（参考01.py的逻辑）
        # 如果所有启用的复选框都被选中，则全选复选框为选中状态
        self.select_all_checkbox.blockSignals(True)
        if enabled_count == 0:
            # 没有启用的复选框，全选复选框设为未选中
            self.select_all_checkbox.setCheckState(Qt.Unchecked)
        elif checked_count == enabled_count:
            # 所有启用的复选框都被选中，全选复选框设为选中
            self.select_all_checkbox.setCheckState(Qt.Checked)
        else:
            # 部分启用的复选框被选中，全选复选框设为未选中（无半选状态）
            self.select_all_checkbox.setCheckState(Qt.Unchecked)
        self.select_all_checkbox.blockSignals(False)
    
    def _add_table_row_with_checkbox(self, row: int, data: list):
        """为表格行添加多选框和序号，然后添加数据"""
        # 第一列：多选框
        # 创建容器，但不设置样式表，避免影响复选框
        check_container = QWidget()
        # 不设置样式表，让容器使用默认样式
        # 设置容器的最小尺寸，确保复选框有足够空间显示
        check_container.setMinimumSize(18, 18)
        check_layout = QVBoxLayout(check_container)
        check_layout.setContentsMargins(0, 0, 0, 0)
        check_layout.setSpacing(0)
        check_layout.setAlignment(Qt.AlignCenter)
        
        # 创建标准复选框控件（完全按照test_checkbox.py的方式，无任何样式表）
        checkbox = QCheckBox()
        # 不设置任何样式表，使用Qt完全默认的样式（与test_checkbox.py完全一致）
        # 确保复选框可见且可交互
        checkbox.setEnabled(True)
        checkbox.setVisible(True)
        checkbox.setCheckable(True)
        
        # 添加状态改变调试
        def debug_state_change(state):
            print(f"第 {row + 1} 行复选框状态改变: {state} (Checked={Qt.Checked}, Unchecked={Qt.Unchecked})")
            print(f"  - isChecked(): {checkbox.isChecked()}")
            print(f"  - checkState(): {checkbox.checkState()}")
            print(f"  - 样式表: {checkbox.styleSheet()[:100] if checkbox.styleSheet() else '空'}")
        
        checkbox.stateChanged.connect(partial(self._on_cell_checkbox_changed, row))
        checkbox.stateChanged.connect(debug_state_change)
        check_layout.addWidget(checkbox)
        
        # 将复选框容器设置到单元格
        self.table_widget.setCellWidget(row, 0, check_container)
        
        # 调试输出（与test_checkbox.py完全一致）
        print(f"添加第 {row + 1} 行复选框，容器大小: {check_container.size()}, 复选框大小: {checkbox.size()}")
        print(f"  - 复选框初始状态: isChecked={checkbox.isChecked()}, checkState={checkbox.checkState()}")

        # 第二列：序号
        index_item = QTableWidgetItem(str(row + 1))
        index_item.setFlags(index_item.flags() & ~Qt.ItemIsEditable)
        index_item.setTextAlignment(Qt.AlignCenter)
        index_item.setForeground(QColor(0, 0, 0))
        self.table_widget.setItem(row, 1, index_item)

        # 其他列：数据（从第3列开始，索引为2）
        for col, cell_data in enumerate(data):
            item = QTableWidgetItem(str(cell_data))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setForeground(QColor(0, 0, 0))
            item.setText(str(cell_data))
            self.table_widget.setItem(row, col + 2, item)
    
    def _setup_works_list_table(self):
        """设置作品列表表格"""
        data_headers = ["作品ID", "作品标题", "作者", "发布时间", "播放量", "点赞数", "状态"]
        self._setup_table_header_with_checkbox(data_headers)
        
        # 设置数据列宽
        self.table_widget.setColumnWidth(2, 100)  # 作品ID
        self.table_widget.setColumnWidth(3, 300)  # 作品标题
        self.table_widget.setColumnWidth(4, 120)  # 作者
        self.table_widget.setColumnWidth(5, 150)  # 发布时间
        self.table_widget.setColumnWidth(6, 100)  # 播放量
        self.table_widget.setColumnWidth(7, 100)  # 点赞数
        self.table_widget.setColumnWidth(8, 100)  # 状态
        
        # 添加示例数据
        sample_data = [
            ["001", "示例作品1", "作者A", "2024-01-01", "1000", "50", "已下载"],
            ["002", "示例作品2", "作者B", "2024-01-02", "2000", "100", "待下载"],
            ["003", "示例作品3", "作者C", "2024-01-03", "3000", "150", "已下载"],
        ]
        
        self.table_widget.setRowCount(len(sample_data))
        for row, row_data in enumerate(sample_data):
            self._add_table_row_with_checkbox(row, row_data)
        
        # 确保表格可见并刷新
        self.table_widget.setVisible(True)
        self.table_widget.viewport().update()  # 刷新视口
    
    def _setup_homepage_extract_table(self):
        """设置主页提取表格"""
        data_headers = ["主页URL", "作者名称", "作品数量", "提取状态", "提取时间"]
        self._setup_table_header_with_checkbox(data_headers)
        
        # 设置数据列宽
        self.table_widget.setColumnWidth(2, 300)  # 主页URL
        self.table_widget.setColumnWidth(3, 150)  # 作者名称
        self.table_widget.setColumnWidth(4, 100)  # 作品数量
        self.table_widget.setColumnWidth(5, 100)  # 提取状态
        self.table_widget.setColumnWidth(6, 150)  # 提取时间
        
        # 添加示例数据
        sample_data = [
            ["https://example.com/user1", "用户1", "50", "已完成", "2024-01-01 10:00"],
            ["https://example.com/user2", "用户2", "30", "进行中", "2024-01-01 11:00"],
            ["https://example.com/user3", "用户3", "20", "待开始", "-"],
        ]
        
        self.table_widget.setRowCount(len(sample_data))
        for row, row_data in enumerate(sample_data):
            self._add_table_row_with_checkbox(row, row_data)
    
    def _setup_single_work_extract_table(self):
        """设置单作品提取表格"""
        data_headers = ["作品URL", "作品标题", "提取状态", "文件路径", "提取时间"]
        self._setup_table_header_with_checkbox(data_headers)
        
        # 添加示例数据
        sample_data = [
            ["https://example.com/work1", "作品标题1", "成功", "/path/to/file1.mp4", "2024-01-01 10:00"],
            ["https://example.com/work2", "作品标题2", "失败", "-", "2024-01-01 10:05"],
        ]
        
        self.table_widget.setRowCount(len(sample_data))
        for row, row_data in enumerate(sample_data):
            self._add_table_row_with_checkbox(row, row_data)
    
    def _setup_keyword_extract_table(self):
        """设置关键词提取表格"""
        data_headers = ["关键词", "搜索结果数", "提取数量", "提取状态", "提取时间"]
        self._setup_table_header_with_checkbox(data_headers)
        
        # 添加示例数据
        sample_data = [
            ["关键词1", "100", "50", "已完成", "2024-01-01 10:00"],
            ["关键词2", "200", "100", "进行中", "2024-01-01 10:05"],
        ]
        
        self.table_widget.setRowCount(len(sample_data))
        for row, row_data in enumerate(sample_data):
            self._add_table_row_with_checkbox(row, row_data)
    
    def _setup_my_homepage_extract_table(self):
        """设置我的主页提取表格"""
        data_headers = ["作品ID", "作品标题", "发布时间", "播放量", "状态"]
        self._setup_table_header_with_checkbox(data_headers)
        
        # 添加示例数据
        sample_data = [
            ["001", "我的作品1", "2024-01-01", "1000", "已提取"],
            ["002", "我的作品2", "2024-01-02", "2000", "已提取"],
        ]
        
        self.table_widget.setRowCount(len(sample_data))
        for row, row_data in enumerate(sample_data):
            self._add_table_row_with_checkbox(row, row_data)
    
    def _setup_universal_browse_extract_table(self):
        """设置万能浏览提取表格"""
        data_headers = ["浏览URL", "提取内容", "提取状态", "提取时间"]
        self._setup_table_header_with_checkbox(data_headers)
        
        # 添加示例数据
        sample_data = [
            ["https://example.com/page1", "内容1", "成功", "2024-01-01 10:00"],
            ["https://example.com/page2", "内容2", "成功", "2024-01-01 10:05"],
        ]
        
        self.table_widget.setRowCount(len(sample_data))
        for row, row_data in enumerate(sample_data):
            self._add_table_row_with_checkbox(row, row_data)
    
    def _setup_default_table(self, menu_item_name: str):
        """设置默认表格（用于其他菜单项）"""
        data_headers = ["项目", "内容", "状态", "时间"]
        self._setup_table_header_with_checkbox(data_headers)
        
        # 添加示例数据
        sample_data = [
            ["项目1", f"{menu_item_name}相关内容1", "正常", "2024-01-01 10:00"],
            ["项目2", f"{menu_item_name}相关内容2", "正常", "2024-01-01 10:05"],
        ]
        
        self.table_widget.setRowCount(len(sample_data))
        for row, row_data in enumerate(sample_data):
            self._add_table_row_with_checkbox(row, row_data)

