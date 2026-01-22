"""
独立进程启动 WebView2(pywebview) 窗口

目的：
- 避免在 Qt 主线程中调用 webview.start() 导致 UI 被阻塞
- 支持同时打开多个浏览器窗口（每个窗口一个进程）
- 复用现有 CookieManager 做自动加载/保存 Cookie（静默）
"""

from __future__ import annotations

import argparse
import hashlib
import time

import webview

from .cookie_manager import CookieManager


DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
)


def main(argv: list[str] | None = None) -> int:
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--title", default="浏览器")
        parser.add_argument("--url", required=True)
        parser.add_argument("--width", type=int, default=1100)
        parser.add_argument("--height", type=int, default=750)
        parser.add_argument("--user-agent", default=DEFAULT_UA)
        args = parser.parse_args(argv)

        print(f"[WebView2 Runner] 启动窗口: {args.title} -> {args.url}")

        cookie_manager = CookieManager()

        window = webview.create_window(
            title=args.title,
            url=args.url,
            width=args.width,
            height=args.height,
            resizable=True,
            fullscreen=False,
            min_size=(800, 600),
            text_select=True,
            background_color="#ffffff",
        )

        print(f"[WebView2 Runner] 窗口已创建，开始启动...")

        # pywebview 的 start 是阻塞的；放在独立进程里就不会影响主程序
        last_cookie_hash = [None]  # 上次 Cookie 的哈希值（用于检测内容变化）
        last_save_time = [0]  # 上次保存时间
        cookies_loaded = [False]  # Cookie 是否已加载
        check_interval = [5.0]  # 检查间隔（秒），登录后缩短为 2 秒
        
        def custom_loop(w: webview.Window):
            current_time = time.time()
            
            try:
                # 第一次循环：加载已保存的 Cookie，并初始化 Cookie 哈希值
                if not cookies_loaded[0]:
                    cookie_manager.apply_cookies_to_webview(w, args.url, verbose=False)
                    cookies_loaded[0] = True
                    last_save_time[0] = current_time
                    
                    # 初始化当前 Cookie 哈希值（避免首次检查误判为"变化"）
                    try:
                        script = """
                        (function() {
                            var cookies = document.cookie.split(';').map(function(c) {
                                return c.trim();
                            }).filter(function(c) {
                                return c.length > 0;
                            }).sort().join('|');
                            return cookies;
                        })();
                        """
                        initial_cookies_str = w.evaluate_js(script) or ""
                        if initial_cookies_str:
                            last_cookie_hash[0] = hashlib.md5(initial_cookies_str.encode('utf-8')).hexdigest()
                    except Exception:
                        pass  # 初始化失败不影响后续检查
                    
                    return False  # 继续循环
                
                # 后续循环：定期检查 Cookie 变化（初始5秒，检测到变化后缩短为2秒）
                if current_time - last_save_time[0] >= check_interval[0]:
                    try:
                        # 获取当前所有 Cookie 并计算哈希值（检测内容变化，不只是数量）
                        script = """
                        (function() {
                            var cookies = document.cookie.split(';').map(function(c) {
                                return c.trim();
                            }).filter(function(c) {
                                return c.length > 0;
                            }).sort().join('|');
                            return cookies;
                        })();
                        """
                        current_cookies_str = w.evaluate_js(script) or ""
                        
                        # 计算 Cookie 字符串的简单哈希（用于快速比较）
                        current_hash = hashlib.md5(current_cookies_str.encode('utf-8')).hexdigest() if current_cookies_str else None
                        
                        # 如果 Cookie 内容有变化（哈希不同），说明可能有新的 Cookie 或值变了（比如用户登录了）
                        if current_hash and current_hash != last_cookie_hash[0]:
                            saved = cookie_manager.save_cookies_from_webview(w, args.url, verbose=False)
                            if saved:
                                # 只有真的发生变化并写入时才提示（等同“登录/状态更新”场景）
                                print("[WebView2 Runner] 检测到 Cookie 变化，已保存")
                                # 检测到变化后，缩短检查间隔（用户可能还在操作）
                                check_interval[0] = 2.0
                            else:
                                # 如果保存失败或内容相同，恢复检查间隔
                                check_interval[0] = 5.0
                            
                            last_cookie_hash[0] = current_hash
                            last_save_time[0] = current_time
                        elif current_hash is None:
                            # 没有 Cookie，重置哈希
                            last_cookie_hash[0] = None
                            check_interval[0] = 5.0
                    except Exception as e:
                        # 调试：打印错误信息
                        print(f"[WebView2 Runner] Cookie 检查出错: {e}")
                
            except Exception as e:
                print(f"[WebView2 Runner] Cookie 操作出错（可忽略）: {e}")

            # 返回 False：继续循环，让窗口一直活着
            return False

        print(f"[WebView2 Runner] 调用 webview.start()...")
        webview.start(func=custom_loop, args=(window,), debug=False, user_agent=args.user_agent)
        print(f"[WebView2 Runner] 窗口已关闭")
        
        # 窗口关闭时，最后保存一次 Cookie（确保不丢失）
        try:
            # 注意：窗口已关闭，无法再获取 Cookie，这里只是提示
            # 实际的 Cookie 保存应该在窗口关闭前完成
            print(f"[WebView2 Runner] 窗口关闭，Cookie 应在关闭前已保存")
        except Exception:
            pass
        
        return 0
    except Exception as e:
        import traceback
        error_msg = f"[WebView2 Runner] 启动失败: {e}\n{traceback.format_exc()}"
        print(error_msg)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


