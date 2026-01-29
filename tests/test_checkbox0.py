"""
测试模块3：完整功能（最终修复版）
"""
import sys
from functools import partial

from PySide6.QtCore import Qt, QTimer, QEventLoop
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

# 优化的表格样式（移除可能导致闪烁的过度样式）
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
    border: none;
    background-color: #c6e2ff;
    color: #000000;
}
QTableWidget::item:selected {
    background-color: #a0d0ff;
    color: #000000;
    border: none;
}
QTableWidget::item:alternate {
    background-color: #d4e8ff;
    border: none;
}
QHeaderView::section {
    background-color: #3498db;
    color: #ffffff;
    padding: 8px;
    border: 1px solid #2980b9;
    font-weight: bold;
    font-size: 13px;
}
"""

BUILTIN_MENU_ITEMS = [
    "作品列表", "主页提取", "单作品提取", "关键词提取", "我的主页提取",
    "万能浏览提取", "下载设置", "VIP中心", "浏览器_登录K", "软件设置",
    "推送消息", "语音转写文案", "使用教程",
]

class CheckboxTestWindow(QMainWindow):
    """多选框测试窗口（最终修复版）"""
    def __init__(self):
        super().__init__()
        self.select_all_checkbox = None
        self.menu_labels: list[QLabel] = []
        self.current_menu_index = 0
        # 防止重复触发的标志
        self.is_updating_checkboxes = False
        # 初始化定时器属性，避免AttributeError
        self._status_timer = None
        self._pos_update_timer = None
        self._select_all_update_timer = None
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("多选框测试页面（最终修复版）")
        self.setGeometry(100, 100, 1200, 800)

        # 禁用窗口大小调整时的自动重绘（减少闪烁）
        self.setUpdatesEnabled(True)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 左侧菜单面板
        left_panel = QWidget()
        left_panel.setFixedWidth(220)
        left_panel.setStyleSheet("""
            QWidget { background: #f7f8fa; }
            QLabel#tool-menu-item {
                padding: 12px 16px;
                border-bottom: 1px solid #e6e8eb;
                color: #2c3e50;
                background: transparent;
            }
            QLabel#tool-menu-item:hover { background: #e7f1ff; }
            QLabel#tool-menu-item[selected="true"] {
                background: #d6e9ff;
                color: #1f6fb2;
                font-weight: bold;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # 创建菜单项（修复点击事件）
        for idx, name in enumerate(BUILTIN_MENU_ITEMS):
            label = QLabel(name)
            label.setObjectName("tool-menu-item")
            label.setProperty("selected", "true" if idx == 0 else "false")
            label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # 修复的点击事件（使用标准方式，避免覆盖mousePressEvent的问题）
            label.mouseReleaseEvent = lambda event, i=idx: self._on_menu_clicked(i)

            left_layout.addWidget(label, 1)
            self.menu_labels.append(label)

        # 右侧内容面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(20)

        # 说明标签
        info_label = QLabel("多选框测试页面（最终修复版）\n- 点击表头复选框可以全选/取消全选\n- 点击行复选框可以单独选择")
        info_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        right_layout.addWidget(info_label)

        # 创建表格（优化渲染）
        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet(TABLE_STYLE)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setShowGrid(False)
        self.table_widget.setGridStyle(Qt.NoPen)

        # 禁用表格的自动滚动（减少闪烁）
        self.table_widget.setAutoScroll(False)

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

    def _on_menu_clicked(self, index: int):
        """菜单项点击处理（修复版）"""
        if not (0 <= index < len(self.menu_labels)) or index == self.current_menu_index:
            return

        self._set_selected(index)

    def _set_selected(self, index: int):
        """优化的菜单项选中逻辑（修复processEvents调用）"""
        # 批量更新样式，减少重绘次数
        self.current_menu_index = index
        for i, label in enumerate(self.menu_labels):
            label.setProperty("selected", "true" if i == index else "false")

        # 修复processEvents调用 - 使用正确的参数
        QApplication.processEvents(QEventLoop.AllEvents)

        # 一次性刷新样式，避免多次重绘
        for label in self.menu_labels:
            label.style().unpolish(label)
            label.style().polish(label)

        item_name = BUILTIN_MENU_ITEMS[index]
        self.update_status(f"选中菜单项: {item_name}")

    def init_table(self):
        """初始化表格（优化版）"""
        headers = ["选择", "序号", "作品ID", "作品标题", "作者", "状态"]
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)

        # 设置第一列表头
        header_item = QTableWidgetItem("")
        header_item.setTextAlignment(Qt.AlignCenter)
        self.table_widget.setHorizontalHeaderItem(0, header_item)

        # 设置列宽
        self.table_widget.setColumnWidth(0, 80)
        self.table_widget.setColumnWidth(1, 60)
        self.table_widget.setColumnWidth(2, 100)
        self.table_widget.setColumnWidth(3, 200)
        self.table_widget.setColumnWidth(4, 120)

        # 添加示例数据
        sample_data = [
            ["001", "示例作品1", "作者A", "已下载"],
            ["002", "示例作品2", "作者B", "待下载"],
            ["003", "示例作品3", "作者C", "已下载"],
            ["004", "示例作品4", "作者D", "待下载"],
            ["005", "示例作品5", "作者E", "已下载"],
        ]

        # 批量添加行，减少UI更新次数
        self.table_widget.setRowCount(len(sample_data))
        self.table_widget.setUpdatesEnabled(False)  # 暂停更新
        for row, row_data in enumerate(sample_data):
            self.add_table_row_with_checkbox(row, row_data)
        self.table_widget.setUpdatesEnabled(True)   # 恢复更新

        # 设置表头全选复选框
        self.setup_header_checkbox()

    def add_table_row_with_checkbox(self, row: int, data: list):
        """优化的行添加逻辑"""
        # 复选框容器
        check_container = QWidget()
        check_container.setMinimumSize(18, 18)
        check_layout = QVBoxLayout(check_container)
        check_layout.setContentsMargins(0, 0, 0, 0)
        check_layout.setSpacing(0)
        check_layout.setAlignment(Qt.AlignCenter)

        # 复选框
        checkbox = QCheckBox()
        checkbox.stateChanged.connect(partial(self.on_cell_checkbox_changed, row))
        check_layout.addWidget(checkbox)
        self.table_widget.setCellWidget(row, 0, check_container)

        # 序号列
        index_item = QTableWidgetItem(str(row + 1))
        index_item.setFlags(index_item.flags() & ~Qt.ItemIsEditable)
        index_item.setTextAlignment(Qt.AlignCenter)
        index_item.setForeground(QColor(0, 0, 0))
        self.table_widget.setItem(row, 1, index_item)

        # 数据列
        for col, cell_data in enumerate(data):
            item = QTableWidgetItem(str(cell_data))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setForeground(QColor(0, 0, 0))
            self.table_widget.setItem(row, col + 2, item)

    def setup_header_checkbox(self):
        """优化的表头复选框设置"""
        self.select_all_checkbox = QCheckBox()
        self.select_all_checkbox.stateChanged.connect(self.on_select_all_changed)

        # 延迟设置（增加延迟时间，确保表头完全渲染）
        QTimer.singleShot(500, self._do_setup_header_checkbox)

    def _do_setup_header_checkbox(self):
        """实际设置表头复选框"""
        if not self.select_all_checkbox or not self.table_widget.horizontalHeader():
            return

        header = self.table_widget.horizontalHeader()
        self.select_all_checkbox.setParent(header)

        # 计算位置（优化）
        x = header.sectionViewportPosition(0) + (header.sectionSize(0) - 18) // 2
        y = (header.height() - 18) // 2
        self.select_all_checkbox.setGeometry(x, y, 18, 18)
        self.select_all_checkbox.show()

        # 连接表头变化信号（去重）
        header.sectionResized.connect(self.update_header_checkbox_position)
        header.sectionMoved.connect(self.update_header_checkbox_position)

    def update_header_checkbox_position(self):
        """更新表头复选框位置（优化）"""
        if not self.select_all_checkbox or not self.table_widget.horizontalHeader():
            return

        # 防止频繁更新
        if self._pos_update_timer is not None and self._pos_update_timer.isActive():
            self._pos_update_timer.stop()

        self._pos_update_timer = QTimer.singleShot(50, self._do_update_header_position)

    def _do_update_header_position(self):
        """实际更新位置"""
        header = self.table_widget.horizontalHeader()
        x = header.sectionViewportPosition(0) + (header.sectionSize(0) - 18) // 2
        y = (header.height() - 18) // 2
        self.select_all_checkbox.move(x, y)

    def on_select_all_changed(self, state):
        """优化的全选逻辑（防止重复触发）"""
        if self.is_updating_checkboxes:
            return

        self.is_updating_checkboxes = True
        is_checked = self.select_all_checkbox.isChecked()

        # 批量更新复选框
        self.table_widget.setUpdatesEnabled(False)
        updated_count = 0
        for row in range(self.table_widget.rowCount()):
            check_container = self.table_widget.cellWidget(row, 0)
            if check_container:
                checkbox = check_container.findChild(QCheckBox)
                if checkbox and checkbox.isEnabled():
                    checkbox.blockSignals(True)
                    checkbox.setChecked(is_checked)
                    checkbox.blockSignals(False)
                    updated_count += 1
        self.table_widget.setUpdatesEnabled(True)

        self.update_status(f"已{'全选' if is_checked else '取消全选'}所有行（共{updated_count}行）")
        self.is_updating_checkboxes = False

    def on_cell_checkbox_changed(self, row: int, state: int):
        """优化的行复选框逻辑"""
        if self.is_updating_checkboxes:
            return

        # 延迟更新全选状态，避免频繁触发
        if self._select_all_update_timer is not None and self._select_all_update_timer.isActive():
            self._select_all_update_timer.stop()

        self._select_all_update_timer = QTimer.singleShot(100, partial(self._do_update_select_all, row))

    def _do_update_select_all(self, row: int):
        """实际更新全选复选框状态"""
        check_container = self.table_widget.cellWidget(row, 0)
        if check_container:
            checkbox = check_container.findChild(QCheckBox)
            if checkbox:
                status = "选中" if checkbox.isChecked() else "取消选中"
                self.update_status(f"第 {row + 1} 行: {status}")

        # 检查所有复选框状态
        total_enabled = 0
        total_checked = 0
        for r in range(self.table_widget.rowCount()):
            container = self.table_widget.cellWidget(r, 0)
            if container:
                cb = container.findChild(QCheckBox)
                if cb and cb.isEnabled():
                    total_enabled += 1
                    if cb.isChecked():
                        total_checked += 1

        # 更新全选复选框
        self.select_all_checkbox.blockSignals(True)
        if total_enabled > 0 and total_checked == total_enabled:
            self.select_all_checkbox.setChecked(True)
        else:
            self.select_all_checkbox.setChecked(False)
        self.select_all_checkbox.blockSignals(False)

    def update_status(self, message: str):
        """优化的状态更新（修复AttributeError）"""
        # 先检查定时器是否存在且处于活动状态
        if self._status_timer is not None and self._status_timer.isActive():
            self._status_timer.stop()

        # 创建新的定时器更新状态
        self._status_timer = QTimer.singleShot(50, lambda: self.status_label.setText(f"状态：{message}"))

def main():
    """主函数（最终修复版）"""
    app = QApplication(sys.argv)

    window = CheckboxTestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()