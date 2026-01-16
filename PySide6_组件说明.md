# PySide6 常用组件与布局说明

> 本文档介绍 PySide6 中常用的 UI 组件和布局方式，用于 WebHarvest 采集工具的界面开发。

---

## 一、基础组件（Widgets）

### 1. 输入框类

#### **QLineEdit** - 单行文本输入框
```python
from PySide6.QtWidgets import QLineEdit

# 创建单行输入框
url_input = QLineEdit()
url_input.setPlaceholderText("请输入URL...")  # 占位提示文字
url_input.setText("https://example.com")      # 设置默认值
text = url_input.text()                       # 获取输入内容
url_input.setMaxLength(200)                   # 限制最大长度
url_input.setReadOnly(True)                   # 只读模式
```

#### **QTextEdit** - 多行文本输入框（富文本）
```python
from PySide6.QtWidgets import QTextEdit

# 创建多行输入框（支持富文本）
text_area = QTextEdit()
text_area.setPlaceholderText("请输入多行文本...")
text_area.setPlainText("第一行\n第二行")      # 纯文本模式
text_area.toPlainText()                       # 获取纯文本内容
text_area.setReadOnly(True)                   # 只读模式（常用于日志显示）
```

#### **QPlainTextEdit** - 多行纯文本输入框（性能更好）
```python
from PySide6.QtWidgets import QPlainTextEdit

# 创建多行纯文本输入框（适合大量文本，性能优于 QTextEdit）
log_view = QPlainTextEdit()
log_view.setReadOnly(True)                    # 只读，用于日志显示
log_view.appendPlainText("新的日志行")        # 追加文本
log_view.clear()                              # 清空内容
```

#### **QSpinBox** - 数字输入框（整数）
```python
from PySide6.QtWidgets import QSpinBox

# 创建整数输入框
thread_count = QSpinBox()
thread_count.setMinimum(1)                    # 最小值
thread_count.setMaximum(100)                 # 最大值
thread_count.setValue(5)                      # 默认值
value = thread_count.value()                  # 获取值
```

#### **QDoubleSpinBox** - 数字输入框（浮点数）
```python
from PySide6.QtWidgets import QDoubleSpinBox

# 创建浮点数输入框
timeout_input = QDoubleSpinBox()
timeout_input.setMinimum(0.1)
timeout_input.setMaximum(300.0)
timeout_input.setSingleStep(0.5)              # 步进值
timeout_input.setDecimals(2)                  # 小数位数
```

#### **QComboBox** - 下拉选择框
```python
from PySide6.QtWidgets import QComboBox

# 创建下拉选择框
engine_select = QComboBox()
engine_select.addItem("Requests引擎")         # 添加选项
engine_select.addItem("QWebEngine引擎")
engine_select.addItem("自动选择")
engine_select.setCurrentIndex(0)              # 设置默认选中项
current_text = engine_select.currentText()    # 获取当前选中文本
current_index = engine_select.currentIndex()  # 获取当前索引
```

#### **QCheckBox** - 复选框
```python
from PySide6.QtWidgets import QCheckBox

# 创建复选框
extract_images = QCheckBox("提取图片")
extract_images.setChecked(True)               # 默认选中
is_checked = extract_images.isChecked()       # 获取选中状态
```

#### **QRadioButton** - 单选按钮（需配合 QButtonGroup）
```python
from PySide6.QtWidgets import QRadioButton, QButtonGroup

# 创建单选按钮组
radio1 = QRadioButton("单代理")
radio2 = QRadioButton("代理池")
radio_group = QButtonGroup()
radio_group.addButton(radio1, 0)
radio_group.addButton(radio2, 1)
radio1.setChecked(True)                       # 默认选中第一个
selected_id = radio_group.checkedId()         # 获取选中ID
```

---

### 2. 按钮类

#### **QPushButton** - 普通按钮
```python
from PySide6.QtWidgets import QPushButton

# 创建按钮
start_btn = QPushButton("开始采集")
start_btn.clicked.connect(self.on_start_clicked)  # 绑定点击事件
start_btn.setEnabled(False)                        # 禁用按钮
start_btn.setEnabled(True)                         # 启用按钮
start_btn.setText("暂停")                          # 修改按钮文字
```

#### **QToolButton** - 工具按钮（可带图标、下拉菜单）
```python
from PySide6.QtWidgets import QToolButton

tool_btn = QToolButton()
tool_btn.setText("更多选项")
tool_btn.setPopupMode(QToolButton.InstantPopup)  # 点击立即弹出菜单
```

---

### 3. 显示类组件

#### **QLabel** - 文本标签
```python
from PySide6.QtWidgets import QLabel

# 创建标签
title_label = QLabel("任务名称:")
title_label.setText("新的文本")                # 设置文本
title_label.setTextFormat(Qt.RichText)         # 支持富文本
title_label.setWordWrap(True)                  # 自动换行
```

#### **QProgressBar** - 进度条
```python
from PySide6.QtWidgets import QProgressBar

# 创建进度条
progress = QProgressBar()
progress.setMinimum(0)                         # 最小值
progress.setMaximum(100)                       # 最大值
progress.setValue(50)                          # 当前值（0-100）
progress.setFormat("%p%")                      # 显示格式（百分比）
progress.setFormat("已处理: %v / %m")          # 自定义格式
```

#### **QTableWidget** - 表格（数据展示）
```python
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

# 创建表格
table = QTableWidget()
table.setColumnCount(4)                        # 设置列数
table.setRowCount(10)                          # 设置行数
table.setHorizontalHeaderLabels(["URL", "状态", "进度", "时间"])  # 表头

# 设置单元格内容
item = QTableWidgetItem("https://example.com")
table.setItem(0, 0, item)                     # 第0行第0列

# 获取单元格内容
cell_item = table.item(0, 0)
if cell_item:
    text = cell_item.text()
```

#### **QListWidget** - 列表（简单列表展示）
```python
from PySide6.QtWidgets import QListWidget, QListWidgetItem

# 创建列表
url_list = QListWidget()
url_list.addItem("https://example1.com")       # 添加项
item = QListWidgetItem("https://example2.com")
url_list.addItem(item)
url_list.currentItem()                         # 获取当前选中项
url_list.takeItem(0)                          # 删除第0项
```

---

### 4. 容器类组件

#### **QGroupBox** - 分组框（带标题的容器）
```python
from PySide6.QtWidgets import QGroupBox

# 创建分组框
proxy_group = QGroupBox("代理配置")
proxy_group.setCheckable(True)                 # 可勾选（启用/禁用整个组）
proxy_group.setChecked(True)                   # 默认启用
```

#### **QTabWidget** - 标签页（多页面切换）
```python
from PySide6.QtWidgets import QTabWidget, QWidget

# 创建标签页容器
tabs = QTabWidget()
tab1 = QWidget()                               # 第一个页面
tab2 = QWidget()                               # 第二个页面
tabs.addTab(tab1, "任务配置")
tabs.addTab(tab2, "代理设置")
current_index = tabs.currentIndex()            # 当前标签页索引
```

#### **QScrollArea** - 滚动区域（内容超出时可滚动）
```python
from PySide6.QtWidgets import QScrollArea, QWidget

scroll = QScrollArea()
content_widget = QWidget()
scroll.setWidget(content_widget)               # 设置可滚动的内容
scroll.setWidgetResizable(True)                # 内容自适应大小
```

---

## 二、布局管理器（Layouts）

### 1. **QVBoxLayout** - 垂直布局（从上到下）
```python
from PySide6.QtWidgets import QVBoxLayout, QWidget

widget = QWidget()
layout = QVBoxLayout()
layout.addWidget(QPushButton("按钮1"))         # 从上到下依次添加
layout.addWidget(QPushButton("按钮2"))
layout.addStretch()                            # 添加弹性空间（推到底部）
widget.setLayout(layout)
```

### 2. **QHBoxLayout** - 水平布局（从左到右）
```python
from PySide6.QtWidgets import QHBoxLayout

layout = QHBoxLayout()
layout.addWidget(QPushButton("左"))
layout.addWidget(QPushButton("中"))
layout.addStretch()                            # 弹性空间（推到右边）
layout.addWidget(QPushButton("右"))
```

### 3. **QGridLayout** - 网格布局（行列网格）
```python
from PySide6.QtWidgets import QGridLayout

layout = QGridLayout()
layout.addWidget(QLabel("URL:"), 0, 0)         # 第0行第0列
layout.addWidget(QLineEdit(), 0, 1)            # 第0行第1列
layout.addWidget(QLabel("代理:"), 1, 0)        # 第1行第0列
layout.addWidget(QLineEdit(), 1, 1)            # 第1行第1列
layout.setColumnStretch(1, 1)                  # 第1列可拉伸
```

### 4. **QFormLayout** - 表单布局（标签+输入框配对）
```python
from PySide6.QtWidgets import QFormLayout

layout = QFormLayout()
layout.addRow("URL:", QLineEdit())             # 自动配对标签和输入框
layout.addRow("代理:", QLineEdit())
layout.addRow("超时:", QSpinBox())
```

### 5. **嵌套布局** - 组合使用
```python
# 主布局（垂直）
main_layout = QVBoxLayout()

# 第一行（水平布局）
row1 = QHBoxLayout()
row1.addWidget(QLabel("URL:"))
row1.addWidget(QLineEdit())
main_layout.addLayout(row1)                   # 将子布局添加到主布局

# 第二行（表单布局）
form_layout = QFormLayout()
form_layout.addRow("代理:", QLineEdit())
main_layout.addLayout(form_layout)
```

---

## 三、主窗口与对话框

### **QMainWindow** - 主窗口（带菜单栏、工具栏、状态栏）
```python
from PySide6.QtWidgets import QMainWindow, QMenuBar, QStatusBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebHarvest 采集工具")
        self.setGeometry(100, 100, 1200, 800)  # x, y, width, height
        
        # 创建菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")
        file_menu.addAction("新建任务", self.new_task)
        file_menu.addAction("导出数据", self.export_data)
        
        # 创建状态栏
        self.statusBar().showMessage("就绪")
        
        # 设置中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
```

### **QDialog** - 对话框（弹窗）
```python
from PySide6.QtWidgets import QDialog, QDialogButtonBox

class ConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("配置")
        layout = QVBoxLayout()
        
        # 对话框内容
        layout.addWidget(QLabel("配置内容..."))
        
        # 标准按钮（确定/取消）
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)  # 确定按钮
        buttons.rejected.connect(self.reject)   # 取消按钮
        layout.addWidget(buttons)
        
        self.setLayout(layout)
```

---

## 四、信号与槽（事件处理）

### 基本用法
```python
from PySide6.QtCore import Qt

# 按钮点击事件
button.clicked.connect(self.on_button_clicked)

def on_button_clicked(self):
    print("按钮被点击")

# 输入框文本改变事件
line_edit.textChanged.connect(self.on_text_changed)

def on_text_changed(self, text):
    print(f"输入内容: {text}")

# 下拉框选择改变事件
combo_box.currentIndexChanged.connect(self.on_selection_changed)

def on_selection_changed(self, index):
    print(f"选中索引: {index}")
```

---

## 五、样式设置（可选）

### 设置窗口样式
```python
# 设置窗口样式表（类似CSS）
self.setStyleSheet("""
    QPushButton {
        background-color: #4CAF50;
        color: white;
        padding: 5px;
        border-radius: 3px;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
    QLineEdit {
        padding: 5px;
        border: 1px solid #ccc;
    }
""")
```

---

## 六、常用组合示例

### 示例1：URL输入 + 添加按钮（水平布局）
```python
url_layout = QHBoxLayout()
url_input = QLineEdit()
add_btn = QPushButton("添加")
url_layout.addWidget(url_input)
url_layout.addWidget(add_btn)
```

### 示例2：任务列表 + 操作按钮（垂直布局）
```python
task_layout = QVBoxLayout()
task_list = QListWidget()
task_layout.addWidget(task_list)

btn_layout = QHBoxLayout()
btn_layout.addWidget(QPushButton("开始"))
btn_layout.addWidget(QPushButton("暂停"))
btn_layout.addWidget(QPushButton("删除"))
task_layout.addLayout(btn_layout)
```

### 示例3：配置面板（分组框 + 表单布局）
```python
group = QGroupBox("代理配置")
form = QFormLayout()
form.addRow("代理地址:", QLineEdit())
form.addRow("端口:", QSpinBox())
form.addRow("用户名:", QLineEdit())
form.addRow("密码:", QLineEdit())
group.setLayout(form)
```

---

## 七、总结

- **输入框**：`QLineEdit`（单行）、`QTextEdit`/`QPlainTextEdit`（多行）、`QSpinBox`（数字）
- **按钮**：`QPushButton`（普通按钮）
- **选择**：`QComboBox`（下拉）、`QCheckBox`（复选框）、`QRadioButton`（单选）
- **显示**：`QLabel`（文本）、`QProgressBar`（进度条）、`QTableWidget`（表格）
- **布局**：`QVBoxLayout`（垂直）、`QHBoxLayout`（水平）、`QGridLayout`（网格）、`QFormLayout`（表单）
- **容器**：`QGroupBox`（分组）、`QTabWidget`（标签页）、`QScrollArea`（滚动区域）
- **窗口**：`QMainWindow`（主窗口）、`QDialog`（对话框）

这些组件和布局足够构建 WebHarvest 的完整界面了！



