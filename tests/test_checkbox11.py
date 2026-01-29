# 抖音浏览器（真内置版）
# 使用 PyQt6.QtWebEngineWidgets 实现真正的浏览器内核内置
# 安装：pip install PyQt6 PyQt6-WebEngine

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# 检查 Python 版本
print(f"Python 版本: {sys.version}")

try:
    from PyQt6.QtCore import Qt, QUrl, QTimer, QSize, QPoint, pyqtSignal, pyqtSlot
    from PyQt6.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QPushButton, QMessageBox, QMainWindow, QFrame, QLineEdit,
        QToolButton, QProgressBar, QSplitter, QCheckBox, QSizePolicy
    )
    from PyQt6.QtGui import QIcon, QFont, QDesktopServices, QPixmap, QColor, QAction
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEnginePage
    
    PYQT6_AVAILABLE = True
    print("✅ PyQt6 模块加载成功")
except ImportError as e:
    PYQT6_AVAILABLE = False
    print(f"⚠️ PyQt6 模块导入错误: {e}")

class WebEngineBrowser(QWebEngineView):
    """增强的 WebEngine 浏览器控件"""
    
    # 自定义信号
    url_changed = pyqtSignal(QUrl)
    title_changed = pyqtSignal(str)
    load_started = pyqtSignal()
    load_finished = pyqtSignal(bool)
    load_progress = pyqtSignal(int)
    console_message = pyqtSignal(str, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_browser()
        self._setup_connections()
    
    def _init_browser(self):
        """初始化浏览器设置"""
        # 设置用户代理（模拟 Chrome）
        profile = QWebEngineProfile.defaultProfile()
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        )
        profile.setHttpUserAgent(user_agent)
        
        # 启用 Cookies 和本地存储
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        profile.setPersistentStoragePath(str(Path.home() / ".cache" / "douyin_browser"))
        
        # 配置页面设置
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, True)
        
        # 禁用自动化控制特征
        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        
        # 设置页面属性
        self.page().profile().setHttpUserAgent(user_agent)
        
        # 注入防检测脚本
        self.page().loadFinished.connect(self._inject_anti_detection)
        
        # 设置 JavaScript 控制台消息处理
        self.page().javaScriptConsoleMessage = self._on_java_script_console_message
    
    def _setup_connections(self):
        """设置信号连接"""
        self.urlChanged.connect(self._on_url_changed)
        self.titleChanged.connect(self._on_title_changed)
        self.loadStarted.connect(self._on_load_started)
        self.loadFinished.connect(self._on_load_finished)
        self.loadProgress.connect(self._on_load_progress)
    
    def _on_url_changed(self, url):
        """URL 变化"""
        self.url_changed.emit(url)
    
    def _on_title_changed(self, title):
        """标题变化"""
        self.title_changed.emit(title)
    
    def _on_load_started(self):
        """开始加载"""
        self.load_started.emit()
    
    def _on_load_finished(self, success):
        """加载完成"""
        self.load_finished.emit(success)
    
    def _on_load_progress(self, progress):
        """加载进度"""
        self.load_progress.emit(progress)
    
    def _on_java_script_console_message(self, level, message, line_number, source_id):
        """JavaScript 控制台消息"""
        level_str = ["DEBUG", "INFO", "WARNING", "ERROR"][level]
        self.console_message.emit(f"[{level_str}] {source_id}:{line_number}: {message}", level)
    
    def _inject_anti_detection(self, success):
        """注入防检测脚本"""
        if not success:
            return
        
        anti_js = """
        (function() {
            console.log('[防检测] 开始注入脚本...');
            
            // === 1. 移除自动化标志 ===
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
                configurable: false,
                enumerable: false
            });
            
            // === 2. 修改插件信息 ===
            const mockPlugins = [{
                description: 'Portable Document Format',
                filename: 'internal-pdf-viewer',
                name: 'Chrome PDF Plugin',
                version: '1.0',
                length: 1
            }];
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => mockPlugins,
                configurable: false
            });
            
            Object.defineProperty(navigator, 'mimeTypes', {
                get: () => [{
                    type: 'application/pdf',
                    suffixes: 'pdf',
                    description: 'Portable Document Format',
                    enabledPlugin: mockPlugins[0]
                }],
                configurable: false
            });
            
            // === 3. 修改语言设置 ===
            Object.defineProperty(navigator, 'language', {
                get: () => 'zh-CN',
                configurable: false
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en-US', 'en'],
                configurable: false
            });
            
            // === 4. 模拟 Chrome 对象 ===
            if (!window.chrome) {
                window.chrome = {
                    runtime: {
                        PlatformOs: { WIN: 1, MAC: 2, LINUX: 3 },
                        id: 'abcdefghijklmnopqrstuvwxyz',
                        getManifest: function() {
                            return { version: '1.0' };
                        },
                        getPlatformInfo: function() {
                            return Promise.resolve({
                                os: 'win',
                                arch: 'x86-64',
                                nacl_arch: 'x86-64'
                            });
                        }
                    },
                    loadTimes: function() {
                        return {
                            requestTime: Date.now() / 1000,
                            startLoadTime: Date.now() / 1000 - 0.1,
                            commitLoadTime: Date.now() / 1000 - 0.05,
                            finishDocumentLoadTime: Date.now() / 1000,
                            finishLoadTime: Date.now() / 1000 + 0.1,
                            firstPaintTime: Date.now() / 1000 + 0.15,
                            navigationType: 'Reload',
                            wasFetchedViaSpdy: true,
                            wasNpnNegotiated: true,
                            npnNegotiatedProtocol: 'h2'
                        };
                    },
                    csi: function() {
                        return {
                            onloadT: Date.now(),
                            startE: Date.now() - 100,
                            pageT: Date.now() - 50,
                            tran: 15
                        };
                    },
                    app: {
                        isInstalled: false,
                        InstallState: { DISABLED: 'disabled' },
                        RunningState: { CANNOT_RUN: 'cannot_run' },
                        getDetails: function() { return null; }
                    },
                    webstore: {
                        onInstallStageChanged: {},
                        onDownloadProgress: {}
                    }
                };
            }
            
            // === 5. 处理 userAgentData ===
            if (navigator.userAgentData) {
                Object.defineProperty(navigator.userAgentData, 'brands', {
                    get: () => [
                        { brand: 'Google Chrome', version: '121' },
                        { brand: 'Chromium', version: '121' },
                        { brand: 'Not?A_Brand', version: '24' }
                    ],
                    configurable: false
                });
                
                Object.defineProperty(navigator.userAgentData, 'platform', {
                    get: () => 'Windows',
                    configurable: false
                });
                
                Object.defineProperty(navigator.userAgentData, 'mobile', {
                    get: () => false,
                    configurable: false
                });
            }
            
            // === 6. 硬件信息模拟 ===
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8,
                configurable: false
            });
            
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8,
                configurable: false
            });
            
            // === 7. 屏幕信息 ===
            Object.defineProperty(screen, 'availWidth', { get: () => 1920 });
            Object.defineProperty(screen, 'availHeight', { get: () => 1040 });
            Object.defineProperty(screen, 'width', { get: () => 1920 });
            Object.defineProperty(screen, 'height', { get: () => 1080 });
            Object.defineProperty(screen, 'colorDepth', { get: () => 24 });
            Object.defineProperty(screen, 'pixelDepth', { get: () => 24 });
            
            // === 8. 移除自动化特征 ===
            ['callPhantom', '_phantom', 'phantom', '__nightmare', 'nightmare',
             '_selenium', 'callSelenium', '_webdriver', '__webdriver',
             '__driver_evaluate', '__fxdriver_evaluate', '__driver_unwrapped',
             '__fxdriver_unwrapped', '_Selenium_IDE_Recorder'].forEach(prop => {
                Object.defineProperty(window, prop, {
                    get: () => undefined,
                    configurable: false
                });
            });
            
            // === 9. 时区设置 ===
            Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {
                value: function() {
                    const result = Intl.DateTimeFormat.prototype.resolvedOptions.call(this);
                    result.timeZone = 'Asia/Shanghai';
                    return result;
                },
                configurable: false
            });
            
            // === 10. 隐藏 Qt 痕迹 ===
            const elements = [navigator, window.chrome, document, window];
            elements.forEach(obj => {
                if (obj && obj.toString) {
                    const originalToString = obj.toString;
                    obj.toString = function() {
                        return originalToString.call(this)
                            .replace(/Qt|WebEngine|PyQt|PySide/gi, '')
                            .replace(/HeadlessChrome/gi, 'Chrome');
                    };
                }
            });
            
            console.log('[防检测] 脚本注入完成！');
            
            // 延迟执行一些额外的修改
            setTimeout(() => {
                // Canvas 指纹干扰
                if (HTMLCanvasElement.prototype.getContext) {
                    const originalGetContext = HTMLCanvasElement.prototype.getContext;
                    HTMLCanvasElement.prototype.getContext = function(contextType) {
                        const context = originalGetContext.apply(this, arguments);
                        if (contextType === '2d') {
                            // 轻微干扰 fillText
                            const originalFillText = context.fillText;
                            context.fillText = function(text, x, y, maxWidth) {
                                return originalFillText.call(this, text, 
                                    x + (Math.random() - 0.5) * 0.01,
                                    y + (Math.random() - 0.5) * 0.01,
                                    maxWidth);
                            };
                        }
                        return context;
                    };
                }
                
                // WebGL 干扰
                if (WebGLRenderingContext && WebGLRenderingContext.prototype.getParameter) {
                    const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
                    WebGLRenderingContext.prototype.getParameter = function(pname) {
                        if (pname === 0x1F00) return 'Google Inc. (NVIDIA)';
                        if (pname === 0x1F01) return 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3060)';
                        return originalGetParameter.call(this, pname);
                    };
                }
                
                console.log('[防检测] 额外修改完成！');
            }, 1000);
        })();
        """
        
        # 执行 JavaScript
        self.page().runJavaScript(anti_js)
    
    def execute_javascript(self, script):
        """执行 JavaScript"""
        self.page().runJavaScript(script)
    
    def clear_cookies(self):
        """清除 Cookies"""
        profile = QWebEngineProfile.defaultProfile()
        cookie_store = profile.cookieStore()
        cookie_store.deleteAllCookies()
    
    def clear_cache(self):
        """清除缓存"""
        profile = QWebEngineProfile.defaultProfile()
        profile.clearHttpCache()

class BrowserToolBar(QWidget):
    """浏览器工具栏"""
    
    def __init__(self, browser_widget, parent=None):
        super().__init__(parent)
        self.browser = browser_widget
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)
        
        # 后退按钮
        self.back_btn = self._create_tool_button("←", "后退 (Alt+Left)")
        self.back_btn.clicked.connect(self.browser.back)
        layout.addWidget(self.back_btn)
        
        # 前进按钮
        self.forward_btn = self._create_tool_button("→", "前进 (Alt+Right)")
        self.forward_btn.clicked.connect(self.browser.forward)
        layout.addWidget(self.forward_btn)
        
        # 刷新按钮
        self.reload_btn = self._create_tool_button("↻", "刷新 (F5)")
        self.reload_btn.clicked.connect(self.browser.reload)
        layout.addWidget(self.reload_btn)
        
        layout.addSpacing(10)
        
        # 主页按钮
        self.home_btn = self._create_tool_button("🏠", "主页 (Alt+Home)")
        self.home_btn.clicked.connect(lambda: self.browser.load(QUrl("https://www.douyin.com")))
        layout.addWidget(self.home_btn)
        
        layout.addSpacing(10)
        
        # URL 输入框
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("输入网址...")
        self.url_edit.setMinimumHeight(32)
        self.url_edit.returnPressed.connect(self._on_url_entered)
        self.url_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 13px;
                background-color: white;
                selection-background-color: #2f80ed;
            }
            QLineEdit:focus {
                border: 2px solid #2f80ed;
                padding: 4px 9px;
            }
        """)
        layout.addWidget(self.url_edit, 1)
        
        # 访问按钮
        self.go_btn = QPushButton("访问")
        self.go_btn.setFixedSize(60, 32)
        self.go_btn.setStyleSheet("""
            QPushButton {
                background-color: #2f80ed;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e6fd9;
            }
            QPushButton:pressed {
                background-color: #1a5fc1;
            }
        """)
        self.go_btn.clicked.connect(self._on_url_entered)
        layout.addWidget(self.go_btn)
        
        # 开发者工具按钮
        self.dev_btn = self._create_tool_button("🔧", "开发者工具 (F12)")
        self.dev_btn.clicked.connect(self._toggle_dev_tools)
        layout.addWidget(self.dev_btn)
    
    def _create_tool_button(self, text, tooltip):
        """创建工具按钮"""
        btn = QPushButton(text)
        btn.setFixedSize(32, 32)
        btn.setToolTip(tooltip)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #ccc;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                color: #999;
                background-color: #f5f5f5;
            }
        """)
        return btn
    
    def _connect_signals(self):
        """连接信号"""
        if self.browser:
            self.browser.url_changed.connect(self._update_url)
            self.browser.load_started.connect(self._on_load_started)
            self.browser.load_finished.connect(self._on_load_finished)
            self.browser.load_progress.connect(self._on_load_progress)
    
    def _update_url(self, url):
        """更新 URL"""
        self.url_edit.setText(url.toString())
    
    def _on_url_entered(self):
        """URL 输入确认"""
        url_text = self.url_edit.text().strip()
        if not url_text:
            return
        
        # 添加协议前缀
        if not url_text.startswith(('http://', 'https://', 'file://', 'about:')):
            url_text = 'https://' + url_text
        
        self.browser.setUrl(QUrl(url_text))
    
    def _on_load_started(self):
        """开始加载"""
        self.go_btn.setText("停止")
        self.go_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
        """)
        self.go_btn.clicked.disconnect()
        self.go_btn.clicked.connect(self.browser.stop)
    
    def _on_load_finished(self, success):
        """加载完成"""
        self.go_btn.setText("访问")
        self.go_btn.setStyleSheet("""
            QPushButton {
                background-color: #2f80ed;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e6fd9;
            }
        """)
        self.go_btn.clicked.disconnect()
        self.go_btn.clicked.connect(self._on_url_entered)
        
        # 更新按钮状态
        self.back_btn.setEnabled(self.browser.history().canGoBack())
        self.forward_btn.setEnabled(self.browser.history().canGoForward())
    
    def _on_load_progress(self, progress):
        """加载进度"""
        # 可以在这里添加进度显示
        pass
    
    def _toggle_dev_tools(self):
        """切换开发者工具"""
        # PyQt6 WebEngine 没有内置的开发者工具
        # 可以使用 F12 快捷键
        self.browser.page().triggerAction(QWebEnginePage.WebAction.InspectElement)

class BuiltinBrowserWindow(QMainWindow):
    """内置浏览器窗口"""
    
    def __init__(self, title="抖音内置浏览器", url="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(1200, 800)
        
        # 设置窗口属性
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 顶部信息栏
        self.info_label = QLabel(f"✅ {title} - 基于 Chromium 内核，无版本过低提示")
        self.info_label.setStyleSheet("""
            QLabel {
                color: #2f80ed;
                background-color: #f0f7ff;
                padding: 8px 20px;
                font-size: 13px;
                border-bottom: 1px solid #e8f4fc;
            }
        """)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.info_label)
        
        # 创建浏览器控件
        self.browser = WebEngineBrowser()
        
        # 创建工具栏
        self.toolbar = BrowserToolBar(self.browser)
        
        # 添加控件
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.browser, 1)
        
        # 状态栏
        self.status_bar = self.statusBar()
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: transparent;
            }
            QProgressBar::chunk {
                background-color: #2f80ed;
            }
        """)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # 连接信号
        self._connect_signals()
        
        # 加载初始 URL
        if url:
            QTimer.singleShot(100, lambda: self.load_url(url))
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        new_window_action = QAction("新建窗口", self)
        new_window_action.setShortcut("Ctrl+N")
        new_window_action.triggered.connect(self._new_window)
        file_menu.addAction(new_window_action)
        
        file_menu.addSeparator()
        
        close_action = QAction("关闭", self)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")
        
        copy_action = QAction("复制", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(lambda: self.browser.page().triggerAction(QWebEnginePage.WebAction.Copy))
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("粘贴", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(lambda: self.browser.page().triggerAction(QWebEnginePage.WebAction.Paste))
        edit_menu.addAction(paste_action)
        
        # 查看菜单
        view_menu = menubar.addMenu("查看")
        
        zoom_in_action = QAction("放大", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self._zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("缩小", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self._zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("重置缩放", self)
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.triggered.connect(self._reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具")
        
        clear_cache_action = QAction("清除缓存", self)
        clear_cache_action.triggered.connect(self.browser.clear_cache)
        tools_menu.addAction(clear_cache_action)
        
        clear_cookies_action = QAction("清除 Cookies", self)
        clear_cookies_action.triggered.connect(self.browser.clear_cookies)
        tools_menu.addAction(clear_cookies_action)
    
    def _connect_signals(self):
        """连接信号"""
        if self.browser:
            self.browser.load_started.connect(self._on_load_started)
            self.browser.load_finished.connect(self._on_load_finished)
            self.browser.load_progress.connect(self._on_load_progress)
            self.browser.title_changed.connect(self._on_title_changed)
            self.browser.console_message.connect(self._on_console_message)
    
    def load_url(self, url):
        """加载 URL"""
        self.browser.setUrl(QUrl(url))
    
    def _new_window(self):
        """新建窗口"""
        new_window = BuiltinBrowserWindow("新建窗口", "https://www.douyin.com")
        new_window.show()
    
    def _zoom_in(self):
        """放大"""
        self.browser.setZoomFactor(self.browser.zoomFactor() + 0.1)
    
    def _zoom_out(self):
        """缩小"""
        self.browser.setZoomFactor(max(0.1, self.browser.zoomFactor() - 0.1))
    
    def _reset_zoom(self):
        """重置缩放"""
        self.browser.setZoomFactor(1.0)
    
    def _on_load_started(self):
        """开始加载"""
        self.status_label.setText("正在加载...")
        self.progress_bar.setRange(0, 0)  # 不确定进度
    
    def _on_load_finished(self, success):
        """加载完成"""
        if success:
            self.status_label.setText("加载完成")
        else:
            self.status_label.setText("加载失败")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        
        # 3秒后隐藏进度条
        QTimer.singleShot(3000, lambda: self.progress_bar.setVisible(False))
    
    def _on_load_progress(self, progress):
        """加载进度"""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(progress)
        self.progress_bar.setVisible(progress < 100)
    
    def _on_title_changed(self, title):
        """标题变化"""
        if title:
            self.setWindowTitle(f"{title} - 抖音内置浏览器")
    
    def _on_console_message(self, message, level):
        """控制台消息"""
        if level >= 2:  # 只显示警告和错误
            print(message)
    
    def closeEvent(self, event):
        """关闭事件"""
        # 清理浏览器资源
        self.browser.deleteLater()
        super().closeEvent(event)

class BrowserLoginPage(QWidget):
    """登录页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._windows = []
        self._setup_ui()
    
    def _setup_ui(self):
        """构建 UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # 标题
        title = QLabel("抖音内置浏览器")
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2f80ed;
                margin-bottom: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # 状态指示
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        status_icon = QLabel("✅" if PYQT6_AVAILABLE else "⚠️")
        status_icon.setFont(QFont("Arial", 24))
        
        status_text = QLabel(
            "Chromium 内核已就绪" if PYQT6_AVAILABLE else
            "PyQt6 模块未安装"
        )
        status_text.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #42b983;
                font-weight: bold;
            }
        """ if PYQT6_AVAILABLE else """
            QLabel {
                font-size: 16px;
                color: #ff6b6b;
                font-weight: bold;
            }
        """)
        
        status_layout.addWidget(status_icon)
        status_layout.addWidget(status_text)
        main_layout.addWidget(status_widget)
        
        # 说明文字
        desc = QLabel("选择要打开的抖音页面，将在内置浏览器中加载，无需担心版本过低提示")
        desc.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                line-height: 1.6;
                text-align: center;
            }
        """)
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(desc)
        
        main_layout.addSpacing(30)
        
        # 按钮容器
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(15)
        
        # 按钮配置
        button_configs = [
            ("🎯 抖音主站登录", "#2f80ed", "优先使用此入口", "https://www.douyin.com/"),
            ("📺 抖音直播页", "#ff6b6b", "直播功能测试", "https://www.douyin.com/live"),
            ("🔍 抖音发现页", "#42b983", "推荐内容测试", "https://www.douyin.com/discover"),
            ("🎬 抖音短视频", "#9b59b6", "视频播放测试", "https://www.douyin.com/video"),
            ("🌐 抖音备用域名", "#3498db", "备用入口", "https://www.iesdouyin.com/"),
            ("⚡ 百度测试", "#e67e22", "网络连接测试", "https://www.baidu.com"),
        ]
        
        for btn_text, color, btn_desc, url in button_configs:
            # 创建按钮容器
            btn_container = QWidget()
            btn_container.setStyleSheet(f"""
                QWidget {{
                    background-color: {color}15;
                    border: 1px solid {color}30;
                    border-radius: 8px;
                    padding: 0px;
                }}
                QWidget:hover {{
                    background-color: {color}25;
                    border-color: {color}50;
                }}
            """)
            
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(15, 10, 15, 10)
            
            # 按钮
            btn = QPushButton(btn_text)
            btn.setMinimumHeight(45)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {color};
                    border: none;
                    border-radius: 6px;
                    font-size: 15px;
                    font-weight: bold;
                    text-align: left;
                    padding-left: 10px;
                }}
                QPushButton:hover {{
                    background-color: {color}20;
                }}
                QPushButton:pressed {{
                    background-color: {color}30;
                }}
            """)
            
            # 描述标签
            desc_label = QLabel(btn_desc)
            desc_label.setStyleSheet(f"""
                QLabel {{
                    color: {color}cc;
                    font-size: 12px;
                    padding-right: 5px;
                }}
            """)
            
            btn_layout.addWidget(btn, 1)
            btn_layout.addWidget(desc_label)
            
            # 连接点击事件
            btn.clicked.connect(lambda _, u=url, t=btn_text.split(" ")[-1]: self._open_browser(u, t))
            
            buttons_layout.addWidget(btn_container)
        
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()
        
        # 底部说明
        bottom_text = QLabel("💡 基于 PyQt6 WebEngine 的真内置浏览器，完全模拟 Chrome 环境")
        bottom_text.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 12px;
                text-align: center;
                padding-top: 20px;
                border-top: 1px solid #eee;
            }
        """)
        bottom_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(bottom_text)
    
    def _open_browser(self, url: str, title: str):
        """打开浏览器窗口"""
        if not PYQT6_AVAILABLE:
            QMessageBox.critical(
                self,
                "错误",
                "PyQt6 模块未安装。\n\n"
                "请运行以下命令安装:\n"
                "pip install PyQt6 PyQt6-WebEngine\n\n"
                "然后重新启动程序。"
            )
            return
        
        browser_win = BuiltinBrowserWindow(f"抖音{title}", url)
        browser_win.show()
        self._windows.append(browser_win)

def check_dependencies():
    """检查依赖"""
    try:
        import PyQt6
        import PyQt6.QtWebEngineWidgets
        return True, "✅ 所有依赖已安装"
    except ImportError as e:
        return False, f"❌ 依赖缺失: {e}"

def main():
    """主函数"""
    print("=" * 50)
    print("抖音内置浏览器 - 启动检查")
    print("=" * 50)
    
    # 检查依赖
    deps_ok, deps_msg = check_dependencies()
    print(deps_msg)
    
    if not deps_ok:
        print("\n请安装依赖:")
        print("pip install PyQt6 PyQt6-WebEngine")
        print("\n按 Enter 键退出...")
        input()
        return
    
    # 设置环境变量（避免某些 Qt 问题）
    os.environ['QT_QPA_PLATFORM'] = 'windows'
    os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-web-security --allow-running-insecure-content'
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("抖音内置浏览器")
    app.setApplicationDisplayName("抖音内置浏览器")
    app.setStyle("Fusion")
    
    # 设置全局样式
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f8f9fa;
        }
        QWidget {
            font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
        }
        QMessageBox {
            font-size: 14px;
        }
    """)
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("抖音内置浏览器")
    main_window.setMinimumSize(600, 700)
    main_window.setCentralWidget(BrowserLoginPage())
    
    # 显示窗口
    main_window.show()
    
    # 运行应用
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n程序错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

