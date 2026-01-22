"""
浏览器登录页面（按钮面板版）
右侧显示"按钮 + 说明文字"的面板，点击按钮弹出独立浏览器窗口打开网址
基于 WebView2（Microsoft Edge 内核）
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)

from ...browser.cookie_storage import CookieStorage
from .browser_popup_window import BrowserPopupWindow


class BrowserLoginPage(QWidget):
    """浏览器登录页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._windows: list[BrowserPopupWindow] = []
        self.cookie_storage = CookieStorage()
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        container = QWidget()
        container.setStyleSheet("QWidget { background-color: #ffffff; }")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(20, 15, 20, 15)
        c_layout.setSpacing(10)

        # 页面说明
        title = QLabel("浏览器登录")
        title.setStyleSheet("QLabel { font-size: 18px; font-weight: bold; color: #333; }")
        c_layout.addWidget(title)

        # 按钮行（左：按钮；右：说明）
        rows = [
            ("打开D音网页", "#2f80ed", "打开网页后，没出现二维码，点击右上角登录，在打开APP扫码登录D音", "https://www.douyin.com/"),
            ("打开D音网页live", "#2f80ed", "【1】备用D音网页打不开，用这个扫码登录", "https://www.douyin.com/live"),
            ("打开D音网页V", "#2f80ed", "【2】备用D音网页打不开，用这个扫码登录", "https://www.douyin.com/"),
            ("打开D音网页(ies)", "#2f80ed", "【3】备用D音网页打不开，用这个扫码登录", "https://www.iesdouyin.com/"),
            ("打开D音网页discover", "#2f80ed", "【4】备用D音网页打不开，用这个扫码登录", "https://www.douyin.com/discover"),
            ("打开D音网页UserSelf", "#2f80ed", "【5】备用D音网页打不开，用这个扫码登录", "https://www.douyin.com/user/self"),
            ("打开D音网页video", "#2f80ed", "【6】备用D音网页打不开，用这个扫码登录", "https://www.douyin.com/video"),
            ("打开百度网页", "#42b983", "用于测试本台电脑能否打开软件浏览器", "https://www.baidu.com"),
            ("打开企查查网页", "#42b983", "用于测试本台电脑能否打开软件浏览器", "https://www.qcc.com"),
        ]

        for text, color, desc, url in rows:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(15)

            btn = QPushButton(text)
            btn.setFixedHeight(34)
            btn.setMinimumWidth(220)
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {color}; color: #ffffff; border: none; font-weight: bold; }}"
                f"QPushButton:hover {{ background-color: {color}; opacity: 0.9; }}"
            )
            btn.clicked.connect(lambda _=False, u=url, t=text: self._open_popup(u, t))
            row_layout.addWidget(btn, 0)

            lbl = QLabel(desc)
            lbl.setStyleSheet(f"QLabel {{ color: {color}; font-size: 12px; }}")
            row_layout.addWidget(lbl, 1, Qt.AlignVCenter)

            c_layout.addWidget(row)

        # 删除缓存按钮
        clear_row = QWidget()
        clear_layout = QHBoxLayout(clear_row)
        clear_layout.setContentsMargins(0, 10, 0, 0)
        clear_layout.setSpacing(15)

        clear_btn = QPushButton("删除浏览器缓存与登录信息")
        clear_btn.setFixedHeight(34)
        clear_btn.setMinimumWidth(220)
        clear_btn.setStyleSheet(
            "QPushButton { background-color: #ff6b6b; color: #ffffff; border: none; font-weight: bold; }"
            "QPushButton:hover { background-color: #ff5252; }"
        )
        clear_btn.clicked.connect(self._clear_cache_and_login)
        clear_layout.addWidget(clear_btn, 0)

        clear_desc = QLabel("缓存太多，提现异常，可适当清理，或，更换D音账号，删除后D音账号自动退出")
        clear_desc.setStyleSheet("QLabel { color: #ff6b6b; font-size: 12px; }")
        clear_layout.addWidget(clear_desc, 1, Qt.AlignVCenter)

        c_layout.addWidget(clear_row)
        c_layout.addStretch()

        layout.addWidget(container)

    def _open_popup(self, url: str, title: str):
        """弹出浏览器窗口打开URL"""
        # 用户要求不显示横幅，避免影响页面（如登录按钮）
        win = BrowserPopupWindow(title="浏览器", banner_text=None, parent=self.window())
        win.open_url(url)
        win.show()
        win.raise_()
        win.activateWindow()
        self._windows.append(win)  # 防止被垃圾回收

    def _clear_cache_and_login(self):
        """清除缓存与登录信息（本地cookie文件）"""
        reply = QMessageBox.question(
            self,
            "确认清理",
            "确定要删除浏览器缓存与登录信息吗？\n（会清空本地保存的Cookie文件）",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        # 删除本地保存的Cookie文件（按域名分离存的json）
        try:
            domains = self.cookie_storage.list_domains()
            for d in domains:
                self.cookie_storage.delete_cookies(d)
            QMessageBox.information(self, "完成", "已清理浏览器登录信息。\n（WebView2 缓存由系统管理，无需手动清理）")
        except Exception as e:
            print(f"删除本地cookie文件失败: {e}")
            QMessageBox.warning(self, "错误", f"清理失败: {e}")
