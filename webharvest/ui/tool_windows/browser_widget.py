"""
浏览器组件
基于 WebView2 的浏览器封装组件，提供 Cookie 管理、加载状态等功能
使用 Microsoft Edge WebView2 内核，支持现代网站（抖音、小红书等）
"""

import threading
from collections.abc import Callable
from urllib.parse import urlparse

import webview

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QProgressBar,
)

from ...browser.cookie_manager import CookieManager


class BrowserWidget(QWidget):
    """浏览器组件 - 封装 WebView2

    注意：WebView2 是独立窗口，不能直接嵌入 Qt Widget
    本组件通过创建独立 WebView2 窗口并提供信号通信来实现浏览器功能

    参数:
        show_navigation: 是否显示导航栏（前进/后退/刷新/地址栏）
        show_status: 是否显示状态栏（进度条/状态/Cookie状态）
    """

    # 信号定义（保持与原有接口兼容）
    url_changed = Signal(str)  # URL改变信号
    load_finished = Signal(bool)  # 加载完成信号
    cookie_saved = Signal(str)  # Cookie保存信号

    def __init__(
        self,
        parent=None,
        show_navigation: bool = True,
        show_status: bool = True,
        user_agent: str | None = None,
        accept_language: str = "zh-CN,zh;q=0.9",
    ):
        super().__init__(parent)

        self.cookie_manager = CookieManager()
        self.current_url = ""
        self.is_logged_in = False
        self._show_navigation = show_navigation
        self._show_status = show_status
        self._user_agent = user_agent
        self._accept_language = accept_language

        # WebView2 窗口实例（独立窗口）
        self.webview_window = None
        self._webview_thread = None
        self._is_loading = False

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """设置UI（占位界面，实际浏览器是独立窗口）"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # 导航栏（即使隐藏也创建，避免属性缺失）
        if self._show_navigation:
            self.nav_widget = self._create_navigation_bar(layout)
        else:
            self.nav_widget = QWidget()
            layout.addWidget(self.nav_widget)
            self.nav_widget.setVisible(False)

        # 占位标签（提示用户浏览器是独立窗口）
        placeholder = QLabel("浏览器将在独立窗口中打开")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("QLabel { color: #666; font-size: 14px; padding: 50px; }")
        layout.addWidget(placeholder)

        # 状态栏（即使隐藏也创建，避免属性缺失）
        if self._show_status:
            self.status_widget = self._create_status_bar(layout)
        else:
            self.status_widget = QWidget()
            layout.addWidget(self.status_widget)
            self.status_widget.setVisible(False)

    def _create_navigation_bar(self, parent_layout):
        """创建导航栏"""
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(5)

        # 后退按钮
        self.back_btn = QPushButton("←")
        self.back_btn.setMaximumWidth(30)
        self.back_btn.clicked.connect(self.go_back)
        nav_layout.addWidget(self.back_btn)

        # 前进按钮
        self.forward_btn = QPushButton("→")
        self.forward_btn.setMaximumWidth(30)
        self.forward_btn.clicked.connect(self.go_forward)
        nav_layout.addWidget(self.forward_btn)

        # 刷新按钮
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setMaximumWidth(30)
        self.refresh_btn.clicked.connect(self.refresh)
        nav_layout.addWidget(self.refresh_btn)

        # URL输入框
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("输入URL...")
        self.url_edit.returnPressed.connect(self._on_url_enter)
        nav_layout.addWidget(self.url_edit)

        # 转到按钮
        self.go_btn = QPushButton("转到")
        self.go_btn.clicked.connect(self._on_url_enter)
        nav_layout.addWidget(self.go_btn)

        parent_layout.addWidget(nav_widget)
        return nav_widget

    def _create_status_bar(self, parent_layout):
        """创建状态栏"""
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(5)

        # 加载进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QLabel("就绪")
        status_layout.addWidget(self.status_label)

        # 弹性空间
        status_layout.addStretch()

        # Cookie状态
        self.cookie_status_label = QLabel("未登录")
        self.cookie_status_label.setStyleSheet("color: #ff6b6b;")
        status_layout.addWidget(self.cookie_status_label)

        parent_layout.addWidget(status_widget)
        return status_widget

    def _setup_connections(self):
        """设置连接（WebView2 通过定时器检查状态）"""
        # 使用定时器定期检查 WebView2 状态
        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._check_webview_status)
        self._status_timer.start(500)  # 每 500ms 检查一次

    def _create_webview_window(self, url: str = ""):
        """创建 WebView2 独立窗口"""
        if self.webview_window is not None:
            return

        # 在独立线程中创建 WebView2 窗口
        def create_window():
            try:
                self.webview_window = webview.create_window(
                    title="浏览器",
                    url=url if url else "about:blank",
                    width=1100,
                    height=750,
                    resizable=True,
                    fullscreen=False,
                    min_size=(800, 600),
                    text_select=True,
                    background_color='#ffffff'
                )

                # 暴露 Python 函数给 JavaScript
                if self.webview_window:
                    # 监听 URL 变化
                    def on_url_changed(new_url):
                        self.current_url = new_url
                        self.url_changed.emit(new_url)
                        if self.url_edit:
                            self.url_edit.setText(new_url)

                    # 监听加载完成
                    def on_load_finished(success):
                        self._is_loading = False
                        self.load_finished.emit(success)
                        self._check_login_status()

                    # 启动 WebView2（阻塞直到窗口关闭）
                    webview.start(debug=False)

            except Exception as e:
                print(f"创建 WebView2 窗口失败: {e}")

        # 在独立线程中运行（避免阻塞主线程）
        self._webview_thread = threading.Thread(target=create_window, daemon=True)
        self._webview_thread.start()

    def _check_webview_status(self):
        """检查 WebView2 窗口状态"""
        if self.webview_window is None:
            return

        try:
            # 检查窗口是否还存在
            if hasattr(self.webview_window, 'destroyed'):
                if self.webview_window.destroyed:
                    self.webview_window = None
                    return

            # 更新 URL（如果窗口存在，通过 JavaScript 获取）
            if self.webview_window:
                try:
                    current_url = self.webview_window.evaluate_js("window.location.href")
                    if current_url and current_url != self.current_url:
                        self.current_url = current_url
                        self.url_changed.emit(current_url)
                        if self.url_edit:
                            self.url_edit.setText(current_url)
                except:
                    pass
        except:
            pass

    def load_url(self, url: str):
        """加载URL"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        self.current_url = url
        self._is_loading = True

        # 如果窗口不存在，创建新窗口
        if self.webview_window is None:
            self._create_webview_window(url)
        else:
            # 如果窗口已存在，导航到新 URL
            try:
                if self.webview_window:
                    self.webview_window.load_url(url)
            except Exception as e:
                print(f"加载 URL 失败: {e}")

        if self.url_edit:
            self.url_edit.setText(url)

        # 更新状态
        if self.progress_bar:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
        if self.status_label:
            self.status_label.setText("加载中...")

    def go_back(self):
        """后退（通过 JavaScript 实现）"""
        if self.webview_window:
            try:
                self.webview_window.evaluate_js("window.history.back()")
            except:
                pass

    def go_forward(self):
        """前进（通过 JavaScript 实现）"""
        if self.webview_window:
            try:
                self.webview_window.evaluate_js("window.history.forward()")
            except:
                pass

    def refresh(self):
        """刷新（通过 JavaScript 实现）"""
        if self.webview_window:
            try:
                self.webview_window.evaluate_js("window.location.reload()")
            except:
                pass

    def _on_url_enter(self):
        """URL输入框回车"""
        url = self.url_edit.text().strip()
        if url:
            self.load_url(url)

    def _check_login_status(self):
        """检查登录状态"""
        if not self.current_url:
            return

        login_status = self.cookie_manager.get_login_status(self.current_url)

        if login_status['has_cookies']:
            self.is_logged_in = True
            if self.cookie_status_label:
                self.cookie_status_label.setText("已登录")
                self.cookie_status_label.setStyleSheet("color: #51cf66;")
        else:
            self.is_logged_in = False
            if self.cookie_status_label:
                self.cookie_status_label.setText("未登录")
                self.cookie_status_label.setStyleSheet("color: #ff6b6b;")

    def save_current_cookies(self) -> bool:
        """保存当前页面的Cookie"""
        if not self.current_url or not self.webview_window:
            return False

        success = self.cookie_manager.save_cookies_from_webview(self.webview_window, self.current_url)
        if success:
            self._check_login_status()
            self.cookie_saved.emit(self.current_url)

        return success

    def apply_saved_cookies(self, url: str) -> bool:
        """应用已保存的Cookie"""
        if not self.webview_window:
            return False

        success = self.cookie_manager.apply_cookies_to_webview(self.webview_window, url)
        if success:
            self._check_login_status()
        return success

    def clear_cookies(self) -> bool:
        """清除当前域名的Cookie"""
        if not self.current_url:
            return False

        success = self.cookie_manager.delete_login_info(self.current_url)
        if success:
            self._check_login_status()

        return success

    def get_current_domain(self) -> str:
        """获取当前域名"""
        return self.cookie_manager.extract_domain_from_url(self.current_url)

    def execute_javascript(self, script: str) -> None:
        """执行JavaScript代码"""
        if self.webview_window:
            try:
                self.webview_window.evaluate_js(script)
            except Exception as e:
                print(f"执行 JavaScript 失败: {e}")

    def get_page_content(self, callback: Callable):
        """获取页面内容"""
        if self.webview_window:
            try:
                script = "document.documentElement.outerHTML"
                content = self.webview_window.evaluate_js(script)
                callback(content)
            except Exception as e:
                print(f"获取页面内容失败: {e}")
                callback("")

    def inject_css(self, css: str) -> None:
        """注入CSS样式"""
        script = f"""
        (function() {{
            var style = document.createElement('style');
            style.textContent = `{css}`;
            document.head.appendChild(style);
        }})();
        """
        self.execute_javascript(script)

    def set_user_agent(self, user_agent: str) -> None:
        """设置User-Agent（WebView2 使用系统默认，此方法保留接口兼容性）"""
        self._user_agent = user_agent
        # WebView2 使用系统 Edge 的 User-Agent，无需手动设置

    def enable_dev_tools(self) -> None:
        """启用开发者工具（WebView2 默认支持 F12）"""
        # WebView2 默认支持 F12 打开开发者工具
        pass
