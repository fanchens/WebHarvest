"""
多选框测试页面
用于单独调试表格中的多选框功能
"""

import sys
from functools import partial

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QCheckBox,
    QLabel,
    QSizePolicy,
)

# 表格样式（修复SVG对勾，确保显示）
TABLE_STYLE = """
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    gridline-color: transparent;
    font-size: 13px;
    border-radius: 0px;
    outline: none;
}
QTableWidget::item {
    padding: 8px;
    border: none !important;
    border-radius: 0px !important;
    background-color: #c6e2ff;
    color: #000000;
    outline: none !important;
    box-shadow: none !important;
}
QTableWidget::item:selected {
    background-color: #a0d0ff;
    color: #000000;
    border: none !important;
    border-radius: 0px !important;
    outline: none !important;
}
QTableWidget::item:hover {
    background-color: #b8d9ff;
    border: none !important;
    border-radius: 0px !important;
    outline: none !important;
}
QTableWidget::item:alternate {
    background-color: #d4e8ff;
    border: none !important;
    border-radius: 0px !important;
    outline: none !important;
}
QHeaderView::section {
    background-color: #3498db;
    color: #ffffff;
    padding: 8px;
    border: 1px solid #2980b9;
    font-weight: bold;
    font-size: 13px;
    border-radius: 0px !important;
}
/* 表格内复选框样式 - 移除所有自定义样式，使用Qt默认样式（与01.py一致） */
"""


# 内置菜单项（固定顺序）
BUILTIN_MENU_ITEMS = [
    "作品列表",
    "主页提取",
    "单作品提取",
    "关键词提取",
    "我的主页提取",
    "万能浏览提取",
    "下载设置",
    "VIP中心",
    "浏览器_登录K",
    "软件设置",
    "推送消息",
    "语音转写文案",
    "使用教程",
]


class CheckboxTestWindow(QMainWindow):
    """多选框测试窗口"""

    def __init__(self):
        super().__init__()
        self.select_all_checkbox = None
        # 左侧菜单相关
        self.menu_labels: list[QLabel] = []
        self.current_menu_index = 0
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("多选框测试页面")
        self.setGeometry(100, 100, 1200, 800)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 根布局（水平布局）
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 左侧菜单面板
        left_panel = QWidget()
        left_panel.setFixedWidth(220)
        left_panel.setStyleSheet(
            """
            QWidget {
                background: #f7f8fa;
            }
            QLabel#tool-menu-item {
                padding: 12px 16px;
                border-bottom: 1px solid #e6e8eb;
                color: #2c3e50;
                background: transparent;
            }
            QLabel#tool-menu-item:hover {
                background: #e7f1ff;
            }
            QLabel#tool-menu-item[selected="true"] {
                background: #d6e9ff;
                color: #1f6fb2;
                font-weight: bold;
            }
            """
        )
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # 创建菜单项
        for idx, name in enumerate(BUILTIN_MENU_ITEMS):
            label = QLabel(name)
            label.setObjectName("tool-menu-item")
            label.setProperty("selected", "true" if idx == 0 else "false")
            label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            def make_handler(i: int):
                def handler(event):
                    QLabel.mousePressEvent(label, event)
                    self._set_selected(i)
                return handler

            label.mousePressEvent = make_handler(idx)
            left_layout.addWidget(label, 1)
            self.menu_labels.append(label)

        # 右侧内容面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(20)

        # 说明标签
        info_label = QLabel("多选框测试页面\n- 点击表头复选框可以全选/取消全选\n- 点击行复选框可以单独选择")
        info_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        right_layout.addWidget(info_label)

        # 创建表格
        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet(TABLE_STYLE)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setShowGrid(False)
        self.table_widget.setGridStyle(Qt.NoPen)

        right_layout.addWidget(self.table_widget)

        # 状态标签
        self.status_label = QLabel("状态：等待操作")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #e8e8e8;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        right_layout.addWidget(self.status_label)

        # 添加左右面板到根布局
        root_layout.addWidget(left_panel)
        root_layout.addWidget(right_panel)

        # 初始化表格
        self.init_table()

    def _set_selected(self, index: int):
        """设置选中的菜单项"""
        if not (0 <= index < len(self.menu_labels)):
            return
        self.current_menu_index = index
        for i, label in enumerate(self.menu_labels):
            label.setProperty("selected", "true" if i == index else "false")
            # 重新应用样式以反映 property 变化
            label.style().unpolish(label)
            label.style().polish(label)
        if index < len(BUILTIN_MENU_ITEMS):
            item_name = BUILTIN_MENU_ITEMS[index]
            print(f"点击菜单项: {item_name}")

    def init_table(self):
        """初始化表格"""
        # 设置列数和表头
        headers = ["选择", "序号", "作品ID", "作品标题", "作者", "状态"]
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)

        # 设置第一列表头为空（用于放置全选复选框）
        header_item = QTableWidgetItem("")
        header_item.setTextAlignment(Qt.AlignCenter)
        self.table_widget.setHorizontalHeaderItem(0, header_item)

        # 设置列宽
        self.table_widget.setColumnWidth(0, 80)   # 选择列
        self.table_widget.setColumnWidth(1, 60)   # 序号列
        self.table_widget.setColumnWidth(2, 100)  # 作品ID
        self.table_widget.setColumnWidth(3, 200)  # 作品标题
        self.table_widget.setColumnWidth(4, 120)  # 作者

        # 添加示例数据
        sample_data = [
            ["001", "示例作品1", "作者A", "已下载"],
            ["002", "示例作品2", "作者B", "待下载"],
            ["003", "示例作品3", "作者C", "已下载"],
            ["004", "示例作品4", "作者D", "待下载"],
            ["005", "示例作品5", "作者E", "已下载"],
        ]

        self.table_widget.setRowCount(len(sample_data))
        for row, row_data in enumerate(sample_data):
            self.add_table_row_with_checkbox(row, row_data)

        # 设置表头全选复选框
        self.setup_header_checkbox()

    def add_table_row_with_checkbox(self, row: int, data: list):
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
        
        # 创建标准复选框控件（完全按照01.py的方式，无任何样式表）
        checkbox = QCheckBox()
        # 不设置任何样式表，使用Qt完全默认的样式（与01.py完全一致）
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
        
        checkbox.stateChanged.connect(partial(self.on_cell_checkbox_changed, row))
        checkbox.stateChanged.connect(debug_state_change)
        check_layout.addWidget(checkbox)
        
        # 将复选框容器设置到单元格
        self.table_widget.setCellWidget(row, 0, check_container)
        
        # 调试输出
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

    def setup_header_checkbox(self):
        """设置表头第一列的全选框（用于全选）"""
        # 创建全选复选框（完全按照01.py的方式，无任何样式表）
        self.select_all_checkbox = QCheckBox()
        # 不设置任何样式表，使用Qt完全默认的样式（与01.py完全一致）
        # 先连接调试，再连接处理函数，确保调试信息在最后
        def debug_state_change(state):
            print(f"\n=== 表头全选复选框状态改变（调试） ===")
            print(f"state: {state}, Qt.Checked={Qt.Checked}, Qt.Unchecked={Qt.Unchecked}")
            print(f"isChecked: {self.select_all_checkbox.isChecked()}")
            print(f"checkState: {self.select_all_checkbox.checkState()}")
        self.select_all_checkbox.stateChanged.connect(debug_state_change)
        # 最后连接处理函数，确保能获取到正确的状态
        self.select_all_checkbox.stateChanged.connect(self.on_select_all_changed)

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
                header.sectionResized.connect(self.update_header_checkbox_position)
                header.sectionMoved.connect(self.update_header_checkbox_position)

        QTimer.singleShot(200, set_header_checkbox)

    def update_header_checkbox_position(self):
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

    def on_select_all_changed(self, state):
        """全选复选框状态改变事件（参考01.py的实现）"""
        # 直接从复选框获取状态，而不是依赖参数（避免信号顺序问题）
        is_checked = self.select_all_checkbox.isChecked()
        print(f"\n=== 执行全选操作 ===")
        print(f"state参数: {state}, Qt.Checked={Qt.Checked}")
        print(f"从复选框获取is_checked: {is_checked}")
        print(f"表格总行数: {self.table_widget.rowCount()}")
        
        self.update_status(f"全选操作: {'全选' if is_checked else '取消全选'}")

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
                        # 阻止信号，避免触发 on_cell_checkbox_changed
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
        # 更新状态显示
        self.update_status(f"已{'全选' if is_checked else '取消全选'}所有行")

    def on_cell_checkbox_changed(self, row: int, state: int = None):
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
                self.update_status(f"第 {row + 1} 行: {status}")
        
        # 使用 QTimer.singleShot(0) 延迟更新，避免在批量设置时频繁触发
        QTimer.singleShot(0, self.update_select_all_checkbox_state)

    def update_select_all_checkbox_state(self):
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

    def update_status(self, message: str):
        """更新状态标签"""
        self.status_label.setText(f"状态：{message}")


def main():
    """主函数"""
    app = QApplication(sys.argv)

    window = CheckboxTestWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()