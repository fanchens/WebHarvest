"""
测试模块3：完整功能（优化版）
"""
import sys
from functools import partial
from typing import Optional

from PySide6.QtCore import Qt, QTimer, QEventLoop, QPoint
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

# ===================== 常量定义（消除魔法数值）=====================
# UI尺寸常量
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
LEFT_PANEL_WIDTH = 220
HEADER_CHECKBOX_SIZE = 18
HEADER_CHECKBOX_OFFSET = 1
TABLE_COLUMN_WIDTHS = [80, 60, 100, 200, 120]

# 定时器延迟常量
HEADER_CHECKBOX_DELAY = 500
POSITION_UPDATE_DELAY = 50
SELECT_ALL_UPDATE_DELAY = 100
STATUS_UPDATE_DELAY = 50

# 样式常量
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

LEFT_PANEL_STYLE = """
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
"""

INFO_LABEL_STYLE = """
QLabel {
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 5px;
    font-size: 12px;
}
"""

STATUS_LABEL_STYLE = """
QLabel {
    background-color: #e8e8e8;
    padding: 10px;
    border-radius: 5px;
    font-size: 12px;
}
"""

# 菜单数据
BUILTIN_MENU_ITEMS = [
    "作品列表", "主页提取", "单作品提取", "关键词提取", "我的主页提取",
    "万能浏览提取", "下载设置", "VIP中心", "浏览器_登录K", "软件设置",
    "推送消息", "语音转写文案", "使用教程",
]

# 示例数据
SAMPLE_DATA = [
    ["001", "示例作品1", "作者A", "已下载"],
    ["002", "示例作品2", "作者B", "待下载"],
    ["003", "示例作品3", "作者C", "已下载"],
    ["004", "示例作品4", "作者D", "待下载"],
    ["005", "示例作品5", "作者E", "已下载"],
]

# 表格表头
TABLE_HEADERS = ["选择", "序号", "作品ID", "作品标题", "作者", "状态"]


class CheckboxTestWindow(QMainWindow):
    """多选框测试窗口（优化版）"""

    def __init__(self):
        super().__init__()
        self.select_all_checkbox: Optional[QCheckBox] = None
        self.menu_labels: list[QLabel] = []
        self.current_menu_index = 0
        self.is_updating_checkboxes = False

        # 定时器管理
        self._status_timer: Optional[QTimer] = None
        self._pos_update_timer: Optional[QTimer] = None
        self._select_all_update_timer: Optional[QTimer] = None

        # UI组件
        self.table_widget: Optional[QTableWidget] = None
        self.status_label: Optional[QLabel] = None

        self.setup_ui()

    def __del__(self):
        """析构函数：清理定时器"""
        self._cleanup_timers()

    def _cleanup_timers(self):
        """清理所有定时器"""
        timers = [self._status_timer, self._pos_update_timer, self._select_all_update_timer]
        for timer in timers:
            if timer and timer.isActive():
                timer.stop()

    def setup_ui(self):
        """设置UI（优化版）"""
        self.setWindowTitle("多选框测试页面（最终修复版）")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 根布局
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 左侧菜单面板
        left_panel = self._create_left_panel()
        # 右侧内容面板
        right_panel = self._create_right_panel()

        # 添加到根布局
        root_layout.addWidget(left_panel)
        root_layout.addWidget(right_panel)

        # 初始化表格
        self.init_table()

    def _create_left_panel(self) -> QWidget:
        """创建左侧菜单面板（模块化重构）"""
        left_panel = QWidget()
        left_panel.setFixedWidth(LEFT_PANEL_WIDTH)
        left_panel.setStyleSheet(LEFT_PANEL_STYLE)

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
            label.mouseReleaseEvent = lambda event, i=idx: self._on_menu_clicked(i)

            left_layout.addWidget(label, 1)
            self.menu_labels.append(label)

        return left_panel

    def _create_right_panel(self) -> QWidget:
        """创建右侧内容面板（模块化重构）"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(20)

        # ========== 关键修改：移除说明标签 ==========
        # 原代码中的info_label已完全删除

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
        self.table_widget.setAutoScroll(False)
        right_layout.addWidget(self.table_widget)

        # 状态标签
        self.status_label = QLabel("状态：等待操作")
        self.status_label.setStyleSheet(STATUS_LABEL_STYLE)
        right_layout.addWidget(self.status_label)

        return right_panel

    def _on_menu_clicked(self, index: int):
        """菜单项点击处理"""
        if not (0 <= index < len(self.menu_labels)) or index == self.current_menu_index:
            return
        self._set_selected(index)

    def _set_selected(self, index: int):
        """设置菜单项选中状态"""
        # 批量更新样式
        self.current_menu_index = index
        for i, label in enumerate(self.menu_labels):
            label.setProperty("selected", "true" if i == index else "false")

        # 处理事件队列
        QApplication.processEvents(QEventLoop.AllEvents)

        # 刷新样式
        for label in self.menu_labels:
            label.style().unpolish(label)
            label.style().polish(label)

        # 更新状态
        item_name = BUILTIN_MENU_ITEMS[index]
        self.update_status(f"选中菜单项: {item_name}")

    def init_table(self):
        """初始化表格"""
        if not self.table_widget:
            return

        # 设置表头
        self.table_widget.setColumnCount(len(TABLE_HEADERS))
        self.table_widget.setHorizontalHeaderLabels(TABLE_HEADERS)

        # 设置表头项
        header_item = QTableWidgetItem("")
        header_item.setTextAlignment(Qt.AlignCenter)
        self.table_widget.setHorizontalHeaderItem(0, header_item)

        # 设置列宽
        for col, width in enumerate(TABLE_COLUMN_WIDTHS):
            self.table_widget.setColumnWidth(col, width)

        # 批量添加行
        self.table_widget.setRowCount(len(SAMPLE_DATA))
        self.table_widget.setUpdatesEnabled(False)
        for row, row_data in enumerate(SAMPLE_DATA):
            self.add_table_row_with_checkbox(row, row_data)
        self.table_widget.setUpdatesEnabled(True)

        # 设置表头全选复选框
        self.setup_header_checkbox()

    def add_table_row_with_checkbox(self, row: int, data: list):
        """添加带复选框的表格行"""
        if not self.table_widget:
            return

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
        """设置表头复选框"""
        self.select_all_checkbox = QCheckBox()
        self.select_all_checkbox.stateChanged.connect(self.on_select_all_changed)

        # 延迟设置
        QTimer.singleShot(HEADER_CHECKBOX_DELAY, self._do_setup_header_checkbox)

    def _do_setup_header_checkbox(self):
        """实际设置表头复选框"""
        if not self.select_all_checkbox or not self.table_widget:
            return

        header = self.table_widget.horizontalHeader()
        if not header:
            return

        self.select_all_checkbox.setParent(header)

        # 计算复选框位置
        x = header.sectionViewportPosition(0) + (header.sectionSize(0) - HEADER_CHECKBOX_SIZE) // 2 - HEADER_CHECKBOX_OFFSET
        y = (header.height() - HEADER_CHECKBOX_SIZE) // 2

        # 设置复选框属性
        self.select_all_checkbox.setAttribute(Qt.WA_NoSystemBackground, True)
        self.select_all_checkbox.setAttribute(Qt.WA_TranslucentBackground, True)
        self.select_all_checkbox.setStyleSheet("QCheckBox { margin: 1px; }")
        self.select_all_checkbox.setGeometry(x, y, HEADER_CHECKBOX_SIZE, HEADER_CHECKBOX_SIZE)
        self.select_all_checkbox.show()

        # 连接表头变化信号
        header.sectionResized.connect(self.update_header_checkbox_position)
        header.sectionMoved.connect(self.update_header_checkbox_position)

    def update_header_checkbox_position(self):
        """更新表头复选框位置"""
        if not self.select_all_checkbox or not self.table_widget:
            return

        # 防抖处理
        if self._pos_update_timer and self._pos_update_timer.isActive():
            self._pos_update_timer.stop()

        self._pos_update_timer = QTimer.singleShot(POSITION_UPDATE_DELAY, self._do_update_header_position)

    def _do_update_header_position(self):
        """实际更新表头复选框位置"""
        if not self.select_all_checkbox or not self.table_widget:
            return

        header = self.table_widget.horizontalHeader()
        if not header:
            return

        # 计算新位置
        x = header.sectionViewportPosition(0) + (header.sectionSize(0) - 16) // 2 - 1
        y = (header.height() - 16) // 2
        self.select_all_checkbox.move(x, y)

    def on_select_all_changed(self, state):
        """全选/取消全选处理"""
        if self.is_updating_checkboxes or not self.table_widget:
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

        # 更新状态
        self.update_status(f"已{'全选' if is_checked else '取消全选'}所有行（共{updated_count}行）")
        self.is_updating_checkboxes = False

    def on_cell_checkbox_changed(self, row: int, state: int):
        """行复选框状态变化处理"""
        if self.is_updating_checkboxes:
            return

        # 防抖处理
        if self._select_all_update_timer and self._select_all_update_timer.isActive():
            self._select_all_update_timer.stop()

        self._select_all_update_timer = QTimer.singleShot(SELECT_ALL_UPDATE_DELAY,
                                                        partial(self._do_update_select_all, row))

    def _do_update_select_all(self, row: int):
        """更新全选复选框状态"""
        if not self.table_widget or not self.select_all_checkbox:
            return

        # 更新单行状态
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
        self.select_all_checkbox.setChecked(total_enabled > 0 and total_checked == total_enabled)
        self.select_all_checkbox.blockSignals(False)

    def update_status(self, message: str):
        """更新状态标签"""
        if not self.status_label:
            return

        # 防抖处理
        if self._status_timer and self._status_timer.isActive():
            self._status_timer.stop()

        self._status_timer = QTimer.singleShot(STATUS_UPDATE_DELAY,
                                             lambda: self.status_label.setText(f"状态：{message}"))

    def closeEvent(self, event):
        """窗口关闭事件：清理资源"""
        self._cleanup_timers()
        super().closeEvent(event)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = CheckboxTestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()