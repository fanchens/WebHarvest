"""
样式配置
存储所有组件的样式定义（保持原有样式和颜色）
"""

# 主窗口样式
MAIN_WINDOW_STYLE = """
QMainWindow {
    background-color: #1a1a2e;
}
QWidget {
    background-color: #1a1a2e;
    color: #ffffff;
}
/* 导航列表样式 */
QListWidget {
    background-color: #f5f5f5;
    border: none;
    color: #333333;
    font-size: 14px;
    font-weight: bold;
    padding: 0px;
    margin: 0px;
    outline: none;
}
QListWidget::item {
    padding: 8px 12px;
    border-radius: 0px;
    margin: 0px;
    background-color: #f5f5f5;
    color: #333333;
    font-weight: bold;
    text-align: center;
}
QListWidget::item:hover {
    background-color: #e8e8e8;
}
QListWidget::item:selected {
    background-color: #5a2e8e;
    color: #ffffff;
    font-weight: bold;
}
QListWidget::item:selected:active {
    background-color: #5a2e8e;
    color: #ffffff;
    font-weight: bold;
}
/* 滚动条样式 */
QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 10px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #cccccc;
    border-radius: 5px;
    min-height: 15px;
}
QScrollBar::handle:vertical:hover {
    background-color: #999999;
}
/* 用户信息标签样式 */
QLabel#user_info_label {
    color: #333333;
    font-size: 13px;
    font-weight: bold;
    padding: 2px 0px;
    background-color: transparent;
}
"""

# 导航项样式
NAV_ITEM_NORMAL_STYLE = """
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
"""

NAV_ITEM_SELECTED_STYLE = """
QLabel {
    padding: 8px 12px;
    background-color: #5a2e8e;
    color: #ffffff;
    font-size: 14px;
    font-weight: bold;
}
"""

# 工具卡片样式
TOOL_CARD_STYLE = """
QFrame {
    background-color: #e8e8e8;
    border: none;
    border-radius: 0px;
    margin: 0px;
    padding: 0px;
}
"""

TOOL_CARD_HEADER_STYLE = """
QWidget {
    background-color: #9b9fc7;
    padding: 0px 15px 0px 2px;
    border: none;
}
"""

TOOL_CARD_STAR_STYLE = "color: #ffffff; font-size: 24px; font-weight: bold; border: none; background-color: transparent; cursor: pointer;"

TOOL_CARD_NAME_STYLE = "color: #ffffff; font-size: 18px; font-weight: bold;"

TOOL_CARD_BUTTON_STYLE = """
QPushButton {
    background-color: transparent;
    color: #ffffff;
    border: none;
    padding: 5px 10px;
    font-size: 18px;
}
QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.2);
}
"""

TOOL_CARD_DESC_STYLE = """
QWidget {
    background-color: #e8e8e8;
    padding: 30px 15px;
}
"""

TOOL_CARD_DESC_TEXT_STYLE = """
color: #333333;
font-size: 24px;
font-weight: bold;
"""

# 用户信息面板样式
USER_PANEL_STYLE = "background-color: #f5f5f5;"

# 底部横幅样式
BANNER_STYLE = "background-color: #1a1a2e;"

BANNER_RED_SECTION_STYLE = "background-color: #ff0000; cursor: pointer;"
BANNER_PURPLE_SECTION_STYLE = "background-color: #9b59b6; cursor: pointer;"
BANNER_BLUE_SECTION_STYLE = "background-color: #3498db; cursor: pointer;"
BANNER_GREEN_SECTION_STYLE = "background-color: #2ecc71; cursor: pointer;"

BANNER_TEXT_STYLE = "color: #ffffff; font-size: 14px; font-weight: bold; border: none; background-color: transparent;"
BANNER_TEXT_SMALL_STYLE = "color: #ffffff; font-size: 12px; font-weight: bold; border: none; background-color: transparent;"
BANNER_TEXT_TINY_STYLE = "color: #ffffff; font-size: 11px; border: none; background-color: transparent;"

# 免责声明卡片样式
DISCLAIMER_CARD_STYLE = """
QFrame {
    background-color: #ffffff;
    border: none;
    border-radius: 0px;
    margin: 0px;
    padding: 0px;
}
"""

DISCLAIMER_TITLE_STYLE = """
color: #333333;
font-size: 20px;
font-weight: bold;
margin-bottom: 10px;
"""

DISCLAIMER_SECTION_TITLE_STYLE = """
color: #333333;
font-size: 16px;
font-weight: bold;
margin-top: 10px;
margin-bottom: 5px;
"""

DISCLAIMER_TEXT_STYLE = """
color: #333333;
font-size: 14px;
line-height: 1.8;
"""

DISCLAIMER_CONTACT_STYLE = """
color: #333333;
font-size: 14px;
margin-top: 20px;
"""

