"""
弹出式浏览器窗口（接口层）

说明：
- pywebview 的 webview.start() 是阻塞调用；如果在 Qt 主线程调用，会导致主界面卡死
- 为了实现“可同时打开多个窗口 + 不阻塞 Qt”，这里改为每次打开都启动一个独立子进程
"""

from __future__ import annotations

import subprocess
import sys
import os
from pathlib import Path


class BrowserPopupWindow:
    """弹出式浏览器窗口 - 基于 WebView2（子进程）"""

    def __init__(self, title: str = "浏览器", banner_text: str | None = None, parent=None):
        self.title = title
        # 保留参数兼容性：用户要求不要横幅，这里不再做任何注入
        self.banner_text = banner_text
        self.parent = parent
        self.current_url = ""
        self._proc: subprocess.Popen | None = None

        # 现代 Chrome User-Agent（避免被识别为旧浏览器）
        self._user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
        )

    def open_url(self, url: str, site_key: str = ""):
        """
        打开指定URL（启动独立子进程，不阻塞 Qt）

        Args:
            url: 要打开的URL
            site_key: 平台标识（如 "douyin", "xiaohongshu"），用于分离不同平台的 profile 目录
        """
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        self.current_url = url

        try:
            # 找到 WebHarvest 目录（包含 webharvest 包的父目录）
            # 当前文件：WebHarvest/webharvest/ui/tool_windows/browser_popup_window.py
            # WebHarvest 目录：当前文件的父目录的父目录的父目录
            current_file = Path(__file__).resolve()
            webharvest_dir = current_file.parent.parent.parent.parent  # WebHarvest 目录
            
            # 验证目录是否存在 webharvest 包
            if not (webharvest_dir / "webharvest" / "__init__.py").exists():
                # 如果找不到，尝试从 sys.path 中找到
                for path in sys.path:
                    webharvest_path = Path(path) / "webharvest"
                    if webharvest_path.exists() and (webharvest_path / "__init__.py").exists():
                        webharvest_dir = Path(path)
                        break
                else:
                    # 如果还是找不到，使用当前工作目录
                    webharvest_dir = Path.cwd()
            
            cmd = [
                sys.executable,
                "-m",
                "webharvest.browser.webview2_runner",
                "--title",
                self.title,
                "--url",
                url,
                "--user-agent",
                self._user_agent,
            ]
            # 如果指定了 site_key，传递给子进程（用于分离不同平台的 profile 目录）
            if site_key:
                cmd.extend(["--site-key", site_key])

            print(f"启动 WebView2 子进程: {' '.join(cmd)}")
            print(f"工作目录: {webharvest_dir}")

            # 暂时不隐藏窗口，方便调试（看到错误信息）
            # Windows 下尽量不弹出黑色控制台窗口
            creationflags = 0
            # 暂时注释掉，方便看到错误
            # if sys.platform.startswith("win"):
            #     creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

            # 设置环境变量，确保能找到 webharvest 模块
            env = os.environ.copy()
            pythonpath = str(webharvest_dir)
            if "PYTHONPATH" in env:
                env["PYTHONPATH"] = pythonpath + os.pathsep + env["PYTHONPATH"]
            else:
                env["PYTHONPATH"] = pythonpath

            self._proc = subprocess.Popen(
                cmd,
                cwd=str(webharvest_dir),  # 设置工作目录
                env=env,  # 设置环境变量
                creationflags=creationflags,
                # 暂时不重定向输出，方便看到错误
                # stdout=subprocess.PIPE,
                # stderr=subprocess.PIPE,
            )
            # 注意：Windows 控制台默认是 GBK，这里避免使用特殊符号（例如 ✓），否则会触发 UnicodeEncodeError
            print(f"[WebView2] 子进程已启动 (PID: {self._proc.pid})")
        except Exception as e:
            import traceback
            error_msg = f"启动 WebView2 子进程失败: {e}\n{traceback.format_exc()}"
            print(error_msg)
            # 尝试显示错误给用户
            try:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(None, "打开浏览器失败", f"无法打开浏览器窗口：\n{str(e)}")
            except:
                pass

    def show(self):
        """兼容接口：子进程窗口会自行显示"""
        pass

    def raise_(self):
        """兼容接口：子进程窗口不受 Qt 控制"""
        pass

    def activateWindow(self):
        """兼容接口：子进程窗口不受 Qt 控制"""
        pass

    # 新增：用于判断浏览器子进程是否仍在运行
    def is_running(self) -> bool:
        """
        内置浏览器是否还在运行（子进程是否存活）
        """
        try:
            return self._proc is not None and self._proc.poll() is None
        except Exception:
            return False


