import webview
import os
import tkinter as tk
from tkinter import messagebox

# ===================== 核心配置 =====================
# 持久化数据存储路径（保存小红书登录Cookie）
USER_DATA_FOLDER = os.path.join(os.path.expanduser("~"), "xiaohongshu_webview_data")
# 确保文件夹存在，不存在则创建
os.makedirs(USER_DATA_FOLDER, exist_ok=True)

# 全局变量：存储WebView2窗口实例
webview_window = None


# ===================== 核心功能函数 =====================
def open_xiaohongshu():
    """打开小红书内置浏览器，保持登录状态（适配pywebview 6.1）"""
    global webview_window
    try:
        # 检查窗口状态：未创建 或 已关闭
        if webview_window is None or getattr(webview_window, 'closed', True):
            # 关键：设置环境变量指定WebView2数据存储目录（6.x版本方式）
            os.environ['WEBVIEW2_USER_DATA_FOLDER'] = USER_DATA_FOLDER

            # 创建WebView2窗口（6.x版本无需指定gui，Windows默认用Edge内核）
            webview_window = webview.create_window(
                title="小红书内置浏览器",
                url="https://www.xiaohongshu.com",  # 小红书网页地址
                width=1000,  # 窗口宽度
                height=800,  # 窗口高度
                resizable=True  # 允许窗口缩放
            )

            # 启动窗口：private_mode=False 是持久化登录的核心（关闭私有模式）
            webview.start(
                debug=False,  # 关闭调试模式（减少日志干扰）
                private_mode=False  # 关键：False=持久化存储，True=临时会话
            )
    except Exception as e:
        # 捕获所有异常并弹窗提示
        messagebox.showerror(
            "启动失败",
            f"错误详情：{str(e)}\n\n解决建议：\n1. 安装WebView2运行时（https://go.microsoft.com/fwlink/p/?LinkId=2124703）\n2. 检查网络是否能访问小红书\n3. 确保路径{USER_DATA_FOLDER}有读写权限"
        )


def close_xiaohongshu():
    """关闭小红书内置浏览器窗口"""
    global webview_window
    try:
        # 检查窗口是否存在且未关闭
        if webview_window and not webview_window.closed:
            webview_window.destroy()  # 关闭窗口
            webview_window = None  # 重置全局变量
            messagebox.showinfo("提示", "小红书窗口已关闭，登录状态已保存到本地！")
    except Exception as e:
        messagebox.showerror("关闭失败", f"错误详情：{str(e)}")


# ===================== 界面入口 =====================
if __name__ == "__main__":
    # 创建tkinter主窗口（按钮界面）
    root = tk.Tk()
    root.title("小红书登录保持工具")  # 窗口标题
    root.geometry("350x150")  # 窗口大小（宽x高）
    root.resizable(False, False)  # 禁止缩放（固定界面大小）

    # 1. 打开小红书按钮
    btn_open = tk.Button(
        root,
        text="打开小红书（保持登录）",
        command=open_xiaohongshu,  # 绑定打开函数
        width=25, height=2,  # 按钮大小
        font=("微软雅黑", 10)  # 字体样式
    )
    btn_open.pack(pady=10)  # 布局：垂直间距10px

    # 2. 关闭小红书按钮
    btn_close = tk.Button(
        root,
        text="关闭小红书",
        command=close_xiaohongshu,  # 绑定关闭函数
        width=25, height=2,  # 按钮大小
        font=("微软雅黑", 10)  # 字体样式
    )
    btn_close.pack(pady=5)  # 布局：垂直间距5px

    # 启动tkinter主循环（保持界面显示）
    root.mainloop()