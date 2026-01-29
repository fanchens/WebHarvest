import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QCheckBox,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel
)
from PySide6.QtCore import Qt


class MultiCheckBoxDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        # 窗口基础设置
        self.setWindowTitle("PySide6 多选复选框组示例")
        self.resize(450, 400)

        # 存储所有复选框的列表（方便批量操作）
        self.checkbox_list = []

        # 创建中心部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # 1. 添加标题
        title_label = QLabel("请选择你喜欢的水果（可多选）：")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        main_layout.addWidget(title_label)

        # 2. 创建复选框组（可多选）
        fruit_list = ["苹果", "香蕉", "橙子", "草莓", "葡萄", "芒果", "西瓜"]
        for fruit in fruit_list:
            cb = QCheckBox(fruit)
            # 给其中一个复选框设置禁用（用于测试跳过禁用逻辑）
            if fruit == "芒果":
                cb.setDisabled(True)
            cb.stateChanged.connect(self.on_single_checkbox_changed)
            self.checkbox_list.append(cb)
            main_layout.addWidget(cb)

        # 3. 功能按钮布局（全选/反选/获取结果）
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 全选按钮
        select_all_btn = QPushButton("全选")
        select_all_btn.clicked.connect(self.select_all_checkboxes)
        button_layout.addWidget(select_all_btn)

        # 取消全选按钮
        deselect_all_btn = QPushButton("取消全选")
        deselect_all_btn.clicked.connect(self.deselect_all_checkboxes)
        button_layout.addWidget(deselect_all_btn)

        # 反选按钮
        invert_select_btn = QPushButton("反选")
        invert_select_btn.clicked.connect(self.invert_select_checkboxes)
        button_layout.addWidget(invert_select_btn)

        # 获取选中结果按钮
        get_selected_btn = QPushButton("获取选中项")
        get_selected_btn.clicked.connect(self.get_selected_checkboxes)
        button_layout.addWidget(get_selected_btn)

        main_layout.addLayout(button_layout)

        # 4. 显示选中结果的标签
        self.result_label = QLabel("已选中：无")
        self.result_label.setStyleSheet("margin-top: 10px; font-size: 14px; color: #666;")
        main_layout.addWidget(self.result_label)

    def on_single_checkbox_changed(self, state):
        """单个复选框状态变化时，更新结果显示"""
        self.update_selected_result()

    def select_all_checkboxes(self):
        """全选所有复选框（跳过禁用的）"""
        for cb in self.checkbox_list:
            # 关键修复：用 isEnabled() 判断是否启用（True=启用，False=禁用）
            if cb.isEnabled():  # 只处理启用的复选框
                cb.setChecked(True)

    def deselect_all_checkboxes(self):
        """取消全选所有复选框"""
        for cb in self.checkbox_list:
            cb.setChecked(False)

    def invert_select_checkboxes(self):
        """反选所有复选框（选中变未选，未选变选中，跳过禁用的）"""
        for cb in self.checkbox_list:
            if cb.isEnabled():  # 关键修复：替换 isDisabled() 为 isEnabled()
                cb.setChecked(not cb.isChecked())

    def get_selected_checkboxes(self):
        """获取所有选中的复选框文本，并打印+显示"""
        selected_items = self.get_selected_items()
        print(f"当前选中的选项：{selected_items}")
        self.update_selected_result()

    def get_selected_items(self):
        """辅助函数：获取所有选中项的文本列表"""
        selected_items = []
        for cb in self.checkbox_list:
            if cb.isChecked():
                selected_items.append(cb.text())
        return selected_items

    def update_selected_result(self):
        """更新界面上的选中结果显示"""
        selected_items = self.get_selected_items()
        if selected_items:
            self.result_label.setText(f"已选中：{', '.join(selected_items)}")
        else:
            self.result_label.setText("已选中：无")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MultiCheckBoxDemo()
    window.show()
    sys.exit(app.exec())