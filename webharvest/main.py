"""
WebHarvest 应用入口

运行方式（开发阶段）：
1）推荐方式（包方式运行）：
    cd E:\\PyCharm\\PythonProject\\WebHarvest
    python -m webharvest.main

2）也支持直接运行本文件（绝对路径）：
    D:\\PyCharm\\python\\python.exe E:\\PyCharm\\PythonProject\\WebHarvest\\webharvest\\main.py
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

# 兼容直接运行本文件的情况：把包根目录加入 sys.path
CURRENT_FILE = Path(__file__).resolve()
PACKAGE_ROOT = CURRENT_FILE.parent.parent  # .../WebHarvest/webharvest -> 上一级 .../WebHarvest
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from webharvest.ui.main_window import MainWindow


def main() -> None:
    """应用入口函数。"""
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()


