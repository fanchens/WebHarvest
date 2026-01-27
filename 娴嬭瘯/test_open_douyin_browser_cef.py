import webview
import sys
import os
import json
import threading
import time
from tkinter import Tk, Button, Frame, Label, messagebox


class DouyinWebView2App:
    """使用WebView2（Edge内核）的内置式浏览器"""

    def __init__(self):
        self.webview_window = None  # WebView2窗口实例
        self.tk_app = None  # Tkinter界面实例
        self.collect_data_flag = False  # 采集数据标记
        self.collected_data = None  # 采集到的数据
        self.running = True  # 程序运行标记

    def create_tkinter_ui(self):
        """创建Tkinter控制界面（运行在子线程）"""
        self.tk_app = Tk()
        self.tk_app.title("抖音采集器 - 内置Edge浏览器")
        self.tk_app.geometry("900x700")

        # 解决Windows高DPI缩放问题
        if sys.platform == "win32":
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass

        # 顶部控制栏
        control_frame = Frame(self.tk_app, bg="#f0f0f0", height=80)
        control_frame.pack(fill="x", padx=10, pady=10)

        # 标题
        title_label = Label(control_frame,
                            text="抖音内置浏览器采集器",
                            font=("微软雅黑", 18, "bold"),
                            bg="#f0f0f0")
        title_label.pack(pady=10)

        # 按钮区域
        btn_frame = Frame(control_frame, bg="#f0f0f0")
        btn_frame.pack()

        # 打开抖音按钮（WebView2已在主线程启动，这里仅提示）
        self.open_btn = Button(btn_frame,
                               text="抖音浏览器已启动",
                               font=("微软雅黑", 12),
                               bg="#6c757d",
                               fg="white",
                               padx=20,
                               pady=10,
                               state="disabled")
        self.open_btn.pack(side="left", padx=10)

        # 采集数据按钮
        self.collect_btn = Button(btn_frame,
                                  text="采集当前页面数据",
                                  font=("微软雅黑", 12),
                                  bg="#28a745",
                                  fg="white",
                                  padx=20,
                                  pady=10,
                                  command=self.trigger_collect_data)
        self.collect_btn.pack(side="left", padx=10)

        # 状态显示
        status_frame = Frame(self.tk_app)
        status_frame.pack(fill="x", padx=10, pady=5)

        self.status_label = Label(status_frame,
                                  text="就绪：WebView2已启动",
                                  font=("微软雅黑", 10),
                                  fg="#666")
        self.status_label.pack()

        # 监听Tkinter关闭事件
        self.tk_app.protocol("WM_DELETE_WINDOW", self.on_tk_close)

        # 运行Tkinter主循环
        self.tk_app.mainloop()

    def on_tk_close(self):
        """关闭Tkinter时终止程序"""
        self.running = False
        if self.webview_window:
            self.webview_window.destroy()
        self.tk_app.destroy()

    def trigger_collect_data(self):
        """触发数据采集（Tkinter子线程调用）"""
        if not self.webview_window:
            messagebox.showerror("错误", "WebView2窗口未启动")
            return

        self.status_label.config(text="正在采集数据...")
        # 标记需要采集数据
        self.collect_data_flag = True

    def collect_page_data(self):
        """采集页面数据（主线程执行）"""
        if not self.collect_data_flag or not self.webview_window:
            return

        try:
            # JavaScript采集代码
            js_code = """
            const pageData = {
                title: document.title,
                url: window.location.href,
                html: document.documentElement.outerHTML.substring(0, 10000),
                text: document.body.innerText.substring(0, 5000),
                timestamp: new Date().toISOString()
            };
            pageData;
            """

            # 执行JS并获取数据（主线程安全）
            self.collected_data = self.webview_window.evaluate_js(js_code)

            if self.collected_data:
                # 保存数据到文件
                save_path = os.path.join(os.getcwd(), "douyin_data.json")
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(self.collected_data, f, ensure_ascii=False, indent=2)

                # 更新Tkinter状态（线程安全）
                if self.tk_app:
                    self.tk_app.after(0, lambda: self.status_label.config(
                        text=f"采集成功：{self.collected_data.get('title', '抖音页面')}"
                    ))
                    self.tk_app.after(0, lambda: messagebox.showinfo(
                        "成功", f"数据已保存到：\n{save_path}"
                    ))
            else:
                if self.tk_app:
                    self.tk_app.after(0, lambda: self.status_label.config(text="采集失败：无数据"))
                    self.tk_app.after(0, lambda: messagebox.showerror("失败", "未采集到页面数据"))

        except Exception as e:
            error_msg = f"采集失败：{str(e)}"
            if self.tk_app:
                self.tk_app.after(0, lambda: self.status_label.config(text=error_msg))
                self.tk_app.after(0, lambda: messagebox.showerror("失败", error_msg))

        finally:
            self.collect_data_flag = False  # 重置采集标记

    def custom_loop(self, window):
        """自定义循环函数（适配pywebview 4.4.1，无interval参数）"""
        while self.running:
            self.collect_page_data()  # 检查并执行采集
            time.sleep(0.1)  # 间隔100ms，替代interval参数
        return False  # 返回False终止循环

    def run(self):
        """主程序入口：主线程运行WebView2，子线程运行Tkinter"""
        # 1. 创建WebView2窗口（主线程）
        self.webview_window = webview.create_window(
            title="抖音 - 内置浏览器",
            url="https://www.douyin.com",
            width=1200,
            height=800,
            resizable=True,
            fullscreen=False,
            min_size=(800, 600),
            confirm_close=True,
            text_select=True,
            background_color='#ffffff'
        )

        # 2. 暴露Python函数给JS（主线程）
        self.webview_window.expose(self.get_page_status)

        # 3. 启动Tkinter界面（子线程，避免阻塞WebView2）
        tk_thread = threading.Thread(target=self.create_tkinter_ui, daemon=True)
        tk_thread.start()

        # 4. 启动WebView2主循环（主线程，核心！）
        # 适配pywebview 4.4.1：移除interval参数，在custom_loop内用time.sleep实现间隔
        webview.start(
            func=self.custom_loop,  # 自定义循环函数
            args=(self.webview_window,),
            debug=True  # 仅保留debug参数，移除interval
        )

    def get_page_status(self):
        """暴露给JS的Python函数"""
        return {
            "status": "running" if self.running else "stopped",
            "message": "WebView2已就绪",
            "url": self.webview_window.get_current_url() if self.webview_window else ""
        }


if __name__ == "__main__":
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误：需要Python 3.8及以上版本")
        sys.exit(1)

    # 强制设置pywebview使用Edge内核（避免版本兼容问题）
    if sys.platform == "win32":
        os.environ["WEBVIEW2_RUNTIME"] = "edge"

    # 启动应用（主线程）
    app = DouyinWebView2App()
    app.run()