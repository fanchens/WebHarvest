"""
布局工具类
包含FlexLayout和FlowLayout
"""

from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLayout,
    QLayoutItem,
    QWidgetItem,
    QBoxLayout,
    QWidget,
)


class FlexLayout:
    """
    通用Flex布局工具类 - 封装QBoxLayout，类似前端Flex布局
    支持：水平/垂直布局、弹性拉伸、对齐方式、间距/内边距
    
    使用示例：
        # 创建垂直Flex布局
        layout = FlexLayout.create(Qt.Vertical, spacing=10, margins=(5,5,5,5))
        
        # 添加弹性控件（flex: 1）
        FlexLayout.add_flex_widget(layout, widget, stretch=1)
    """
    
    @staticmethod
    def create(direction: Qt.Orientation = Qt.Vertical,
               spacing: int = 0,
               margins: tuple = (0, 0, 0, 0),
               alignment: Qt.AlignmentFlag = Qt.Alignment()) -> QBoxLayout:
        """
        创建Flex布局
        :param direction: 布局方向（Qt.Vertical=垂直，Qt.Horizontal=水平）
        :param spacing: 控件间距（对应flex的gap）
        :param margins: 内边距 (left, top, right, bottom)
        :param alignment: 整体对齐方式（默认空对齐，即拉伸填充）
        :return: QBoxLayout对象
        """
        layout = QVBoxLayout() if direction == Qt.Vertical else QHBoxLayout()
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        if alignment:
            layout.setAlignment(alignment)
        return layout

    @staticmethod
    def add_flex_widget(layout: QBoxLayout,
                        widget: QWidget,
                        stretch: int = 0,
                        alignment: Qt.AlignmentFlag = Qt.Alignment()) -> None:
        """
        添加弹性控件到布局（对应flex: stretch值）
        :param layout: 目标布局
        :param widget: 要添加的控件
        :param stretch: 拉伸比例（对应flex: 1/2/3...）
        :param alignment: 控件在布局中的对齐方式
        """
        layout.addWidget(widget, stretch=stretch, alignment=alignment)


class FlowLayout(QLayout):
    """
    流式布局 - 类似CSS Flexbox的wrap效果
    支持自动换行、间距控制、对齐方式
    """
    
    def __init__(self, parent=None, spacing=5, margin=5):
        super().__init__(parent)
        self._items = []
        self._spacing = spacing
        self._margin = margin
        self._alignment = Qt.AlignTop | Qt.AlignLeft
    
    def addItem(self, item: QLayoutItem):
        """添加布局项"""
        self._items.append(item)
    
    def addWidget(self, widget: QWidget):
        """添加控件"""
        self.addItem(QWidgetItem(widget))
        self.invalidate()  # 触发布局更新
    
    def count(self):
        """返回布局项数量"""
        return len(self._items)
    
    def itemAt(self, index: int):
        """获取指定索引的布局项"""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
    
    def takeAt(self, index: int):
        """移除并返回指定索引的布局项"""
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None
    
    def setSpacing(self, spacing: int):
        """设置间距"""
        self._spacing = spacing
        self.invalidate()
    
    def setMargin(self, margin: int):
        """设置边距"""
        self._margin = margin
        self.invalidate()
    
    def setAlignment(self, alignment: Qt.AlignmentFlag):
        """设置对齐方式"""
        self._alignment = alignment
        self.invalidate()
    
    def sizeHint(self):
        """返回布局的建议大小"""
        return self._do_layout(QRect(), test_only=True)
    
    def minimumSizeHint(self):
        """返回布局的最小大小"""
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self._margin, 2 * self._margin)
        return size
    
    def setGeometry(self, rect: QRect):
        """设置布局几何形状"""
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)
    
    def _do_layout(self, rect: QRect, test_only: bool):
        """执行布局计算 - 支持2列布局"""
        if not self._items:
            return QSize(2 * self._margin, 2 * self._margin)
        
        # 获取父容器的实际宽度（优先使用父容器宽度，否则使用rect宽度）
        parent_widget = self.parent()
        if parent_widget and hasattr(parent_widget, 'width'):
            container_width = parent_widget.width()
        else:
            container_width = rect.width()
        
        # 如果宽度为0，使用默认值
        if container_width <= 0:
            container_width = 800
        
        # 计算可用宽度和每列宽度（2列布局）
        available_width = container_width - 2 * self._margin
        # 每列宽度 = (可用宽度 - 中间间距) / 2
        column_width = (available_width - self._spacing) // 2 if available_width > 0 else 400
        
        x = rect.x() + self._margin
        y = rect.y() + self._margin
        line_height = 0
        max_width = 0
        items_per_line = 0
        space_x = self._spacing
        space_y = self._spacing
        
        # 动态导入ToolCard，避免循环导入
        from webharvest.ui.widgets.tool_card import ToolCard
        
        for item in self._items:
            if item is None:
                continue
                
            widget = item.widget()
            if widget is None:
                continue
            
            # 检查widget是否仍然有效（避免访问已删除的对象）
            try:
                if not widget.isVisible() and not test_only:
                    # 跳过不可见的widget，但允许在test_only模式下计算
                    pass
            except RuntimeError:
                # widget已被删除，跳过
                continue
            
            # 如果是ToolCard，使用计算出的列宽度
            if isinstance(widget, ToolCard):
                item_width = column_width
                item_height = 150  # 固定高度
                # 检查是否需要换行（每行2个）
                if items_per_line >= 2:
                    # 换行
                    x = rect.x() + self._margin
                    y = y + line_height + space_y
                    items_per_line = 0
                    line_height = 0
            else:
                # 非ToolCard（如免责声明卡片），占据整个宽度
                item_width = available_width
                # 对于非ToolCard，使用sizeHint计算高度，如果无效则使用最小高度提示
                item_height = 400  # 默认高度
                try:
                    # 先检查widget是否仍然有效
                    if widget:
                        size_hint = item.sizeHint()
                        if size_hint and size_hint.height() > 0:
                            item_height = size_hint.height()
                        else:
                            min_size = item.minimumSize()
                            if min_size and min_size.height() > 0:
                                item_height = min_size.height()
                            else:
                                # 尝试从widget获取
                                try:
                                    widget_hint = widget.sizeHint()
                                    if widget_hint and widget_hint.height() > 0:
                                        item_height = widget_hint.height()
                                except (RuntimeError, AttributeError):
                                    pass
                except (RuntimeError, AttributeError):
                    # 如果访问失败，使用默认高度
                    pass
                # 确保宽度至少是可用宽度
                if item_width <= 0:
                    item_width = available_width if available_width > 0 else 800
                # 如果是第一个非ToolCard，或者需要换行，从新行开始
                if items_per_line > 0:
                    x = rect.x() + self._margin
                    y = y + line_height + space_y
                    items_per_line = 0
                    line_height = 0
            
            if not test_only:
                try:
                    item.setGeometry(QRect(x, y, item_width, item_height))
                except RuntimeError:
                    # 如果设置几何形状失败，跳过
                    continue
            
            x = x + item_width + space_x
            line_height = max(line_height, item_height)
            max_width = max(max_width, x - space_x)
            items_per_line += 1
        
        return QSize(max_width + self._margin, y + line_height + self._margin)
    
    def expandingDirections(self):
        """返回布局的扩展方向"""
        return Qt.Orientations(Qt.Orientation(0))

