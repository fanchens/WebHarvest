from __future__ import annotations

"""
小红书采集入口（最小可跑）

用法：
  在 WebHarvest 目录下运行：
    python -m webharvest.collectors.xiaohongshu.run --login

说明：
- 这里复用现有 WebView2(pywebview) runner 的启动方式
- 先做验证链路：能打开小红书、登录后 Cookie 能被保存、并定期落一个页面快照
"""

import argparse
import time

import webview

from webharvest.browser.cookie_manager import CookieManager
from webharvest.browser.webview2_runner import DEFAULT_UA
from webharvest.collectors.xiaohongshu.config import XHSConfig
from webharvest.collectors.xiaohongshu.tasks.snapshot import take_page_snapshot


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="")
    parser.add_argument("--login", action="store_true", help="打开登录/发现页（建议先扫码登录一次）")
    parser.add_argument("--title", default="小红书采集")
    parser.add_argument("--user-agent", default=DEFAULT_UA)
    args = parser.parse_args(argv)

    cfg = XHSConfig()
    url = args.url or (cfg.login_url if args.login else cfg.base_url)

    cookie_manager = CookieManager()

    window = webview.create_window(
        title=args.title,
        url=url,
        width=1100,
        height=750,
        resizable=True,
        fullscreen=False,
        min_size=(800, 600),
        text_select=True,
        background_color="#ffffff",
    )

    # 用 custom loop 做两件事：
    # 1) 首次加载：应用已保存 Cookie（如果有）
    # 2) 轮询：保存 Cookie（仅变化时才写盘）+ 定期落 snapshot
    cookies_loaded = [False]
    last_snapshot = [0.0]

    def custom_loop(w: webview.Window):
        now = time.time()
        try:
            if not cookies_loaded[0]:
                cookie_manager.apply_cookies_to_webview(w, url, verbose=False)
                cookies_loaded[0] = True

            # 让 CookieManager 自己做“是否变化”的判断（内部已做指纹对比）
            cookie_manager.save_cookies_from_webview(w, url, verbose=False)

            # 每 8 秒落一个快照（便于确认当前页面/标题/是否有 cookie）
            if now - last_snapshot[0] >= 8.0:
                take_page_snapshot(w, user_agent=args.user_agent, save=True)
                last_snapshot[0] = now
        except Exception:
            pass

        return False

    webview.start(func=custom_loop, args=(window,), debug=False, user_agent=args.user_agent)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


