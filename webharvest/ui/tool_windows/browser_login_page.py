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
from ...browser.profile_path import get_webview2_profile_dir
from ..common.confirm_dialog import ConfirmIcon, ConfirmOptions, confirm
from .browser_popup_window import BrowserPopupWindow


class BrowserLoginPage(QWidget):
    """浏览器登录页面"""

    def __init__(self, parent=None, *, tool_name: str = "", site_key: str = ""):
        super().__init__(parent)
        self._windows: list[BrowserPopupWindow] = []
        self.cookie_storage = CookieStorage()
        self._tool_name = tool_name or ""
        self._site_key = site_key or ""
        self._setup_ui()

    def _has_open_browser_windows(self) -> bool:
        """
        是否仍有内置浏览器窗口处于打开状态
        - 删除缓存前做一次简单检查，避免在使用中强制清理
        """
        for win in self._windows:
            try:
                if win is not None and getattr(win, "is_running", None):
                    if win.is_running():
                        return True
            except RuntimeError:
                # Qt 已销毁的窗口访问可能抛错，忽略即可
                continue
        return False

    @staticmethod
    def _infer_site_key(tool_name: str) -> str:
        """根据工具名粗略推断站点 key（用于显示不同登录链接）"""
        t = (tool_name or "").lower()
        if "douyin" in t:
            return "douyin"
        if "xiaohongshu" in t or "xhs" in t:
            return "xiaohongshu"
        if "kuaishou" in t:
            return "kuaishou"
        return "default"

    def _get_rows(self):
        """返回当前页面应显示的按钮行（按站点区分）"""
        site = self._site_key or self._infer_site_key(self._tool_name)

        if site == "xiaohongshu":
            return [
                ("打开小红书首页", "#e74c3c", "打开后可扫码/手机号登录（如未出现登录入口，先点右上角头像/登录）", "https://www.xiaohongshu.com/"),
                ("打开小红书发现页", "#e74c3c", "常用入口：发现/探索内容", "https://www.xiaohongshu.com/explore"),
                ("打开小红书搜索页", "#e74c3c", "用于测试搜索入口是否可用", "https://www.xiaohongshu.com/search_result"),
                ("打开百度网页", "#42b983", "用于测试本台电脑能否打开软件浏览器", "https://www.baidu.com"),
            ]

        if site == "kuaishou":
            return [
                ("打开快手首页", "#ff7a00", "打开后可扫码/账号登录", "https://www.kuaishou.com/"),
                ("打开快手视频页", "#ff7a00", "用于测试视频详情页入口", "https://www.kuaishou.com/"),
                ("打开百度网页", "#42b983", "用于测试本台电脑能否打开软件浏览器", "https://www.baidu.com"),
            ]

        # 默认：抖音（现有逻辑）
        return [
            ("打开抖音网页", "#2f80ed", "打开网页后，没出现二维码，点击右上角登录，再打开APP扫码登录抖音", "https://www.douyin.com/"),
            ("打开抖音网页live", "#2f80ed", "【1】备用抖音网页打不开，用这个扫码登录", "https://www.douyin.com/live"),
            ("打开抖音网页V", "#2f80ed", "【2】备用抖音网页打不开，用这个扫码登录", "https://www.douyin.com/"),
            ("打开抖音网页(ies)", "#2f80ed", "【3】备用抖音网页打不开，用这个扫码登录", "https://www.iesdouyin.com/"),
            ("打开抖音网页discover", "#2f80ed", "【4】备用抖音网页打不开，用这个扫码登录", "https://www.douyin.com/discover"),
            ("打开抖音网页UserSelf", "#2f80ed", "【5】备用抖音网页打不开，用这个扫码登录", "https://www.douyin.com/user/self"),
            ("打开抖音网页video", "#2f80ed", "【6】备用抖音网页打不开，用这个扫码登录", "https://www.douyin.com/video"),
            ("打开百度网页", "#42b983", "用于测试本台电脑能否打开软件浏览器", "https://www.baidu.com"),
            ("打开企查查网页", "#42b983", "用于测试本台电脑能否打开软件浏览器", "https://www.qcc.com"),
        ]

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
        rows = self._get_rows()

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

        clear_desc = QLabel("缓存太多，提现异常，可适当清理，或，更换抖音账号，删除后抖音账号自动退出")
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
        from pathlib import Path
        import shutil

        # 0) 如内置浏览器窗口仍在打开，先提示用户关闭
        if self._has_open_browser_windows():
            confirm(
                self,
                ConfirmOptions(
                    title="无法清理",
                    message="检测到内置浏览器窗口仍在打开中，请先关闭内置浏览器，再尝试删除缓存与登录信息。",
                    icon=ConfirmIcon.WARNING,
                    ok_text="知道了",
                    cancel_text="关闭",
                    default_to_cancel=False,
                ),
            )
            return

        # 1) 检查本地 Cookie 文件（域名级 JSON）
        try:
            domains = self.cookie_storage.list_domains()
        except Exception as e:
            print(f"读取本地 cookie 列表失败: {e}")
            QMessageBox.warning(self, "错误", f"清理失败: {e}")
            return

        # 2) 检查 WebView2 浏览器缓存目录
        profile_dir = get_webview2_profile_dir()
        profile_path = Path(profile_dir)
        has_profile_dir = profile_path.exists() and any(profile_path.iterdir())

        has_cookie_files = bool(domains)

        # 既没有 Cookie 文件，也没有浏览器缓存目录内容：在这一弹窗里提示“无需删除”
        if not has_cookie_files and not has_profile_dir:
            confirm(
                self,
                ConfirmOptions(
                    title="确认清理",
                    message="当前没有已保存的浏览器缓存与登录信息，无需删除。",
                    icon=ConfirmIcon.INFO,
                    ok_text="知道了",
                    cancel_text="关闭",
                    default_to_cancel=False,
                ),
            )
            return

        # 有任意一类数据时：弹出危险操作确认框
        ok = confirm(
            self,
            ConfirmOptions(
                title="确认清理",
                message="确定要删除浏览器缓存与登录信息吗？",
                icon=ConfirmIcon.WARNING,
                ok_text="确定",
                cancel_text="取消",
                default_to_cancel=True,
            ),
        )
        if not ok:
            return

        # 先清 Cookie 文件
        try:
            for d in domains:
                self.cookie_storage.delete_cookies(d)
        except Exception as e:
            print(f"删除本地 cookie 文件失败: {e}")
            QMessageBox.warning(self, "错误", f"清理失败: {e}")
            return

        # 再清 WebView2 缓存目录（如存在）
        try:
            if profile_path.exists():
                shutil.rmtree(profile_path, ignore_errors=True)
        except Exception as e:
            print(f"删除 WebView2 缓存目录失败: {e}")
            # 缓存删不干净不算致命，不再额外弹窗
