"""
工具窗口样式配置
"""

# 工具窗口整体样式
TOOL_WINDOW_STYLE = """
QMainWindow {
    background-color: #ffffff;
}
"""

# 顶部标题栏样式
TOOL_WINDOW_HEADER_STYLE = """
QWidget {
    background-color: #ffffff;
    border-bottom: 1px solid #e0e0e0;
}
"""

# 左侧菜单容器样式
TOOL_WINDOW_MENU_CONTAINER_STYLE = """
QWidget {
    background-color: #3498db;
}
"""

# 菜单项样式 - 未选中状态
TOOL_WINDOW_MENU_ITEM_NORMAL_STYLE = """
QLabel {
    background-color: #3498db;
    color: #ffffff;
    font-size: 14px;
    font-weight: bold;
    padding: 12px 20px;
    border: none;
}
QLabel:hover {
    background-color: #2980b9;
}
"""

# 菜单项样式 - 选中状态
TOOL_WINDOW_MENU_ITEM_SELECTED_STYLE = """
QLabel {
    background-color: #ff69b4;
    color: #ffffff;
    font-size: 14px;
    font-weight: bold;
    padding: 12px 20px;
    border: none;
}
"""

# 右侧内容区域样式
TOOL_WINDOW_CONTENT_STYLE = """
QWidget {
    background-color: #f5f5f5;
}
"""

# 表格样式（与test_checkbox.py完全一致）
TOOL_WINDOW_TABLE_STYLE = """
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
/* 确保复选框容器和复选框本身不受全局样式影响 */
QTableWidget QWidget {
    background-color: transparent;
}
QTableWidget QCheckBox {
    background-color: transparent;
}
"""

