import subprocess
import sys
import os
import time
from tkinter import Tk, Button, messagebox

# 解决Windows高DPI和中文显示问题
if sys.platform == "win32":
    import ctypes

    ctypes.windll.shcore.SetProcessDpiAwareness(1)


class DouyinNativeBrowser:
    """直接调用本地Chrome的抖音浏览器（零伪装）"""

    def __init__(self):
        self.chrome_process = None
        self.root = Tk()
        self.root.title("抖音浏览器（原生Chrome内核）")
        self.root.geometry("800x500")
        self.root.resizable(False, False)

        # 创建核心按钮
        self.start_btn = Button(
            self.root,
            text="打开抖音（原生Chrome）",
            font=("微软雅黑", 18),
            bg="#0084ff",
            fg="white",
            padx=30,
            pady=15,
            command=self.launch_douyin
        )
        self.start_btn.pack(expand=True)

        self.stop_btn = Button(
            self.root,
            text="关闭抖音浏览器",
            font=("微软雅黑", 18),
            bg="#ff3333",
            fg="white",
            padx=30,
            pady=15,
            command=self.close_douyin,
            state="disabled"
        )
        self.stop_btn.pack(expand=True, pady=20)

    def find_local_chrome(self):
        """查找本地Chrome的真实路径"""
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.join(os.environ["LOCALAPPDATA"], "Google\Chrome\Application\chrome.exe")
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                return path
        return None

    def launch_douyin(self):
        """启动抖音（Chrome应用模式，无地址栏，像内置）"""
        chrome_path = self.find_local_chrome()
        if not chrome_path:
            messagebox.showerror("错误", "未找到本地Chrome浏览器，请先安装Chrome")
            return

        # Chrome应用模式参数（关键：无地址栏、无菜单，视觉上就是内置浏览器）
        chrome_args = [
            chrome_path,
            "--app=https://www.douyin.com",  # 应用模式，隐藏浏览器框架
            "--window-size=1300,900",  # 窗口尺寸
            "--window-position=100,100",  # 窗口位置
            "--no-default-browser-check",  # 禁用默认浏览器提示
            "--no-first-run",  # 禁用首次运行提示
            "--disable-blink-features=AutomationControlled"  # 消除自动化指纹
        ]

        try:
            # 启动Chrome（和本地Chrome共用所有配置/缓存/登录状态）
            self.chrome_process = subprocess.Popen(chrome_args)
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            messagebox.showinfo("成功", "抖音浏览器已启动（复用本地Chrome内核）")
        except Exception as e:
            messagebox.showerror("启动失败", f"原因：{str(e)}")

    def close_douyin(self):
        """关闭抖音浏览器进程"""
        if self.chrome_process and self.chrome_process.poll() is None:
            self.chrome_process.terminate()
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            messagebox.showinfo("成功", "抖音浏览器已关闭")

    def run(self):
        """运行主窗口"""
        self.root.mainloop()


if __name__ == "__main__":
    # 启动程序
    browser = DouyinNativeBrowser()
    browser.run()