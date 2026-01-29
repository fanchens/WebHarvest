"""
数据表格组件（公共表格）

设计目标：
- 前两列固定：**选择**(复选框)、**序号**
- 后续列动态：不同页面可传入不同的表头/列宽/数据字段
"""

from functools import partial
from typing import Sequence

from PySide6.QtCore import Qt, QTimer, QEventLoop, QPoint
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QCheckBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)

# ===================== 表格相关常量 ======================
# 表格样式
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

# ===================== 表格 schema（前两列固定，后续列动态） ======================
BASE_HEADERS = ["选择", "序号"]
BASE_COLUMN_WIDTHS = [80, 60]

# 默认动态列（保持当前 UI 行为不变）
DEFAULT_EXTRA_HEADERS = ["作品ID", "作品标题", "作者", "状态"]
DEFAULT_EXTRA_WIDTHS = [100, 200, 120, 120]

SAMPLE_DATA = [
    ["001", "示例作品1", "作者A", "已下载"],
    ["002", "示例作品2", "作者B", "待下载"],
    ["003", "示例作品3", "作者C", "已下载"],
    ["004", "示例作品4", "作者D", "待下载"],
    ["005", "示例作品5", "作者E", "已下载"],
]

# 定时器延迟常量
HEADER_CHECKBOX_DELAY = 100
POSITION_UPDATE_DELAY = 50
SELECT_ALL_UPDATE_DELAY = 100

# UI尺寸常量
HEADER_CHECKBOX_SIZE = 18
HEADER_CHECKBOX_OFFSET = 1


class DataTableWidget(QTableWidget):
    """数据表格组件 - 支持复选框管理和数据展示"""

    def __init__(
        self,
        parent=None,
        *,
        extra_headers: Sequence[str] | None = None,
        extra_widths: Sequence[int] | None = None,
    ):
        super().__init__(parent)
        self.select_all_checkbox: QCheckBox | None = None
        self.is_updating_checkboxes = False
        self._extra_headers: list[str] = list(extra_headers) if extra_headers is not None else list(DEFAULT_EXTRA_HEADERS)
        self._extra_widths: list[int] = list(extra_widths) if extra_widths is not None else list(DEFAULT_EXTRA_WIDTHS)

        # 定时器管理
        self._pos_update_timer: QTimer | None = None
        self._select_all_update_timer: QTimer | None = None

        # 初始化表格
        self._setup_table()
        self._load_sample_data()

    def __del__(self):
        """析构函数：清理定时器"""
        self._cleanup_timers()

    def _cleanup_timers(self):
        """清理所有定时器"""
        timers = [self._pos_update_timer, self._select_all_update_timer]
        for timer in timers:
            if timer and timer.isActive():
                timer.stop()

    def _setup_table(self):
        """设置表格基本属性"""
        # 设置样式和属性
        self.setStyleSheet(TABLE_STYLE)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setGridStyle(Qt.NoPen)
        self.setAutoScroll(False)

        # 设置尺寸策略
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 设置表头（前两列固定，后续列动态）
        headers = self.get_headers()
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

        # 设置表头项
        header_item = QTableWidgetItem("")
        header_item.setTextAlignment(Qt.AlignCenter)
        self.setHorizontalHeaderItem(0, header_item)

        # 设置列宽（最后一列自动拉伸）
        widths = self.get_column_widths()
        for col, width in enumerate(widths[:-1]):
            self.setColumnWidth(col, width)

        # 设置表头全选复选框
        self.setup_header_checkbox()

    def get_headers(self) -> list[str]:
        """返回当前 schema 的完整表头"""
        return list(BASE_HEADERS) + list(self._extra_headers)

    def get_column_widths(self) -> list[int]:
        """返回当前 schema 的完整列宽"""
        # 宽度不足时用默认值兜底；超出则截断
        extra_widths = list(self._extra_widths)[: len(self._extra_headers)]
        if len(extra_widths) < len(self._extra_headers):
            extra_widths += [120] * (len(self._extra_headers) - len(extra_widths))
        return list(BASE_COLUMN_WIDTHS) + extra_widths

    def set_schema(
        self,
        *,
        extra_headers: Sequence[str],
        extra_widths: Sequence[int] | None = None,
        clear_rows: bool = True,
    ):
        """
        重新设置动态列 schema（前两列固定不变）
        - extra_headers: 动态列表头
        - extra_widths: 动态列列宽（可选）
        - clear_rows: 是否清空行数据（默认清空）
        """
        self._extra_headers = list(extra_headers)
        if extra_widths is not None:
            self._extra_widths = list(extra_widths)

        # 先断开/清理旧的表头复选框，避免残留
        if self.select_all_checkbox:
            try:
                self.select_all_checkbox.setParent(None)
                self.select_all_checkbox.deleteLater()
            except Exception:
                pass
            self.select_all_checkbox = None

        if clear_rows:
            self.setRowCount(0)

        # 重建表头与列宽
        headers = self.get_headers()
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

        widths = self.get_column_widths()
        for col, width in enumerate(widths[:-1]):
            self.setColumnWidth(col, width)

        # 重建全选复选框
        self.setup_header_checkbox()

    def _load_sample_data(self):
        """加载示例数据"""
        self.setRowCount(len(SAMPLE_DATA))
        self.setUpdatesEnabled(False)

        for row, row_data in enumerate(SAMPLE_DATA):
            self.add_table_row_with_checkbox(row, row_data)

        self.setUpdatesEnabled(True)

    def add_table_row_with_checkbox(self, row: int, data: list):
        """
        添加带复选框的表格行
        data: 仅包含“动态列”的数据（不包含 选择/序号）
        """
        # 复选框容器
        check_container = QWidget()
        check_container.setMinimumSize(18, 18)
        check_container.setStyleSheet("QWidget { background-color: transparent; }")
        check_layout = QVBoxLayout(check_container)
        check_layout.setContentsMargins(0, 0, 0, 0)
        check_layout.setSpacing(0)
        check_layout.setAlignment(Qt.AlignCenter)

        # 复选框
        checkbox = QCheckBox()
        checkbox.setStyleSheet("QCheckBox { background-color: transparent; }")
        checkbox.stateChanged.connect(partial(self.on_cell_checkbox_changed, row))
        check_layout.addWidget(checkbox)
        self.setCellWidget(row, 0, check_container)

        # 序号列
        index_item = QTableWidgetItem(str(row + 1))
        index_item.setFlags(index_item.flags() & ~Qt.ItemIsEditable)
        index_item.setTextAlignment(Qt.AlignCenter)
        index_item.setForeground(QColor(0, 0, 0))
        self.setItem(row, 1, index_item)

        # 数据列（按当前 schema 的动态列数填充；不足补空，超出截断）
        extra_col_count = len(self._extra_headers)
        normalized = list(data)[:extra_col_count]
        if len(normalized) < extra_col_count:
            normalized += [""] * (extra_col_count - len(normalized))

        for col, cell_data in enumerate(normalized):
            item = QTableWidgetItem(str(cell_data))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setForeground(QColor(0, 0, 0))
            self.setItem(row, col + 2, item)

    def setup_header_checkbox(self):
        """设置表头复选框"""
        self.select_all_checkbox = QCheckBox()
        self.select_all_checkbox.stateChanged.connect(self.on_select_all_changed)

        # 延迟设置
        QTimer.singleShot(HEADER_CHECKBOX_DELAY, self._do_setup_header_checkbox)

    def _do_setup_header_checkbox(self):
        """实际设置表头复选框"""
        if not self.select_all_checkbox:
            return

        header = self.horizontalHeader()
        if not header:
            return

        self.select_all_checkbox.setParent(header)

        # 计算复选框位置
        x = header.sectionViewportPosition(0) + (header.sectionSize(0) - HEADER_CHECKBOX_SIZE) // 2 - HEADER_CHECKBOX_OFFSET
        y = (header.height() - HEADER_CHECKBOX_SIZE) // 2

        # 设置复选框属性
        self.select_all_checkbox.setAttribute(Qt.WA_NoSystemBackground, True)
        self.select_all_checkbox.setAttribute(Qt.WA_TranslucentBackground, True)
        self.select_all_checkbox.setStyleSheet("QCheckBox { margin: 1px; background-color: transparent; }")
        self.select_all_checkbox.setGeometry(x, y, HEADER_CHECKBOX_SIZE, HEADER_CHECKBOX_SIZE)
        self.select_all_checkbox.show()

        # 连接表头变化信号
        header.sectionResized.connect(self.update_header_checkbox_position)
        header.sectionMoved.connect(self.update_header_checkbox_position)

    def update_header_checkbox_position(self):
        """更新表头复选框位置"""
        if not self.select_all_checkbox:
            return

        # 防抖处理
        if self._pos_update_timer and self._pos_update_timer.isActive():
            self._pos_update_timer.stop()

        self._pos_update_timer = QTimer.singleShot(POSITION_UPDATE_DELAY, self._do_update_header_position)

    def _do_update_header_position(self):
        """实际更新表头复选框位置"""
        if not self.select_all_checkbox:
            return

        header = self.horizontalHeader()
        if not header:
            return

        # 计算新位置
        x = header.sectionViewportPosition(0) + (header.sectionSize(0) - 16) // 2 - 1
        y = (header.height() - 16) // 2
        self.select_all_checkbox.move(x, y)

    def on_select_all_changed(self, state):
        """全选/取消全选处理"""
        if self.is_updating_checkboxes:
            return

        self.is_updating_checkboxes = True
        is_checked = self.select_all_checkbox.isChecked()

        # 批量更新复选框
        self.setUpdatesEnabled(False)
        updated_count = 0

        for row in range(self.rowCount()):
            check_container = self.cellWidget(row, 0)
            if check_container:
                checkbox = check_container.findChild(QCheckBox)
                if checkbox and checkbox.isEnabled():
                    checkbox.blockSignals(True)
                    checkbox.setChecked(is_checked)
                    checkbox.blockSignals(False)
                    updated_count += 1

        self.setUpdatesEnabled(True)

        print(f"已{'全选' if is_checked else '取消全选'}所有行（共{updated_count}行）")
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
        if not self.select_all_checkbox:
            return

        # 更新单行状态
        check_container = self.cellWidget(row, 0)
        if check_container:
            checkbox = check_container.findChild(QCheckBox)
            if checkbox:
                status = "选中" if checkbox.isChecked() else "取消选中"
                print(f"第 {row + 1} 行: {status}")

        # 检查所有复选框状态
        total_enabled = 0
        total_checked = 0

        for r in range(self.rowCount()):
            container = self.cellWidget(r, 0)
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

    def get_selected_rows(self) -> list[int]:
        """获取选中的行号列表"""
        selected_rows = []
        for row in range(self.rowCount()):
            check_container = self.cellWidget(row, 0)
            if check_container:
                checkbox = check_container.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_rows.append(row)
        return selected_rows

    def load_data(self, data: list[list[str]]):
        """加载自定义数据"""
        self.setRowCount(len(data))
        self.setUpdatesEnabled(False)

        for row, row_data in enumerate(data):
            self.add_table_row_with_checkbox(row, row_data)

        self.setUpdatesEnabled(True)

    def clear_data(self):
        """清空表格数据"""
        self.setRowCount(0)
        # 清理复选框状态
        if self.select_all_checkbox:
            self.select_all_checkbox.setChecked(False)
