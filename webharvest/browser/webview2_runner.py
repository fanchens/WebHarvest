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
from pathlib import Path
import time
import os
import threading
import subprocess

import webview

from .cookie_manager import CookieManager
from .profile_path import get_webview2_profile_dir


DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
)


def start_edge_monitor() -> None:
    """
    尝试通过轮询 tasklist 检测本机上新增的 Edge(msedge.exe) 进程，仅用于粗略判断是否有外部 Edge 被拉起。
    说明：
    - 只能在 Windows 下工作；
    - 只能看到“有新的 Edge 进程出现”，不能百分之百确认一定是当前 WebView2 导致；
    - 主要用于调试/观测，不影响主流程。
    """
    if os.name != "nt":
        return

    seen_pids: set[str] = set()

    def scan_once() -> None:
        nonlocal seen_pids
        try:
            # 只筛选 msedge.exe 进程
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            output = subprocess.check_output(
                ["tasklist", "/FI", "IMAGENAME eq msedge.exe"],
                creationflags=creationflags,
            ).decode("utf-8", errors="ignore")

            current_pids: set[str] = set()
            for line in output.splitlines():
                # 典型行格式：msedge.exe                 12345 Console                    1     200,000 K
                if "msedge.exe" in line.lower():
                    parts = line.split()
                    if parts and parts[0].lower() == "msedge.exe" and len(parts) >= 2:
                        pid = parts[1]
                        if pid.isdigit():
                            current_pids.add(pid)

            # 找出本轮中新出现的 Edge 进程
            new_pids = current_pids - seen_pids
            for pid in sorted(new_pids):
                print(f"[WebView2 Runner] [Edge监控] 检测到新的 Edge 进程: PID={pid}")

            seen_pids |= current_pids
        except subprocess.CalledProcessError:
            # tasklist 调用失败直接忽略，不影响主流程
            pass
        except Exception as e:
            print(f"[WebView2 Runner] [Edge监控] 检测失败: {e}")

    # 先跑一轮，记录当前已存在的 Edge 进程，避免把历史进程当成“新打开”
    scan_once()

    def loop() -> None:
        while True:
            time.sleep(2.0)
            scan_once()

    t = threading.Thread(target=loop, name="EdgeMonitor", daemon=True)
    t.start()


def main(argv: list[str] | None = None) -> int:
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--title", default="浏览器")
        parser.add_argument("--url", required=True)
        parser.add_argument("--width", type=int, default=1100)
        parser.add_argument("--height", type=int, default=750)
        parser.add_argument("--user-agent", default=DEFAULT_UA)
        parser.add_argument("--site-key", default="", help="平台标识（如 douyin, xiaohongshu），用于分离不同平台的 profile 目录")
        args = parser.parse_args(argv)

        print(f"[WebView2 Runner] 启动窗口: {args.title} -> {args.url}")

        cookie_manager = CookieManager()

        # 统一 WebView2 user_data 目录，按平台分离（方便后续按平台清理缓存 + 保持登录状态）
        site_key = args.site_key.strip() if args.site_key else None
        profile_dir = get_webview2_profile_dir(site_key=site_key)
        try:
            Path(profile_dir).mkdir(parents=True, exist_ok=True)
            # 对 WebView2 来说，使用环境变量 WEBVIEW2_USER_DATA_FOLDER 指定缓存目录
            os.environ["WEBVIEW2_USER_DATA_FOLDER"] = str(profile_dir)
            if site_key:
                print(f"[WebView2 Runner] 使用平台 profile 目录: {profile_dir}")
        except Exception:
            # 目录/环境变量设置失败不致命，只是后续无法统一清理
            pass

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
        check_interval = [5.0]  # 智能轮询间隔（秒）：初始5秒，检测到变化缩短为2秒，没变化逐渐延长到最多30秒
        cookie_saved_on_close = [False]  # 窗口关闭时是否已保存Cookie
        
        # 注册 Python API 供 JS 调用（窗口关闭前保存Cookie）
        def save_cookies_on_close():
            """窗口关闭前保存Cookie（由JS的beforeunload事件调用）"""
            try:
                if not cookie_saved_on_close[0]:
                    print("[WebView2 Runner] [窗口关闭前] 开始保存Cookie...")
                    saved = cookie_manager.save_cookies_from_webview(window, args.url, verbose=True)
                    if saved:
                        cookie_saved_on_close[0] = True
                        print("[WebView2 Runner] [窗口关闭前] Cookie已保存")
                    else:
                        print("[WebView2 Runner] [窗口关闭前] 未检测到Cookie变化，无需保存")
            except Exception as e:
                print(f"[WebView2 Runner] [窗口关闭前] 保存Cookie失败: {e}")

        def log_link_event(kind: str, url: str | None = None, detail: str | None = None):
            """供 JS 调用的链接事件日志：区分内置/外置/被拦截等情况"""
            try:
                url_str = url or ""
                detail_str = detail or ""
                print(f"[WebView2 Runner] [链接事件] {kind} | url={url_str} | detail={detail_str}")
            except Exception:
                # 打印失败直接忽略，避免影响主流程
                pass

        # 暴露Python函数给JS调用
        window.expose(save_cookies_on_close)
        window.expose(log_link_event)
        
        def custom_loop(w: webview.Window):
            current_time = time.time()
            
            try:
                # 第一次循环：加载已保存的 Cookie，并初始化 Cookie 哈希值，注入窗口关闭监听
                if not cookies_loaded[0]:
                    # 第一次循环：尝试加载已保存的 Cookie
                    loaded = cookie_manager.apply_cookies_to_webview(w, args.url, verbose=True)
                    print(f"[WebView2 Runner] [初始化] 初次加载Cookie，结果: {loaded}")
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
                            print(f"[WebView2 Runner] [初始化] 当前Cookie哈希: {last_cookie_hash[0][:8]}...")
                    except Exception:
                        pass  # 初始化失败不影响后续检查
                    
                    # 注入JS代码：监听窗口关闭事件 + 使用更严格的融合拦截逻辑
                    try:
                        inject_script = """
                        (function() {
                            // 1. 监听窗口关闭前保存Cookie
                            window.addEventListener('beforeunload', function() {
                                try {
                                    if (window.pywebview && window.pywebview.api && window.pywebview.api.save_cookies_on_close) {
                                        window.pywebview.api.save_cookies_on_close();
                                    }
                                } catch (e) {
                                    console.error('保存Cookie失败:', e);
                                }
                            });

                            // 2. 融合版拦截逻辑：只拦截「有风险/会跳外置浏览器」的情况 + 打印所有点击
                            try {
                                // 避免重复注入
                                if (!window.__inner_intercept) {
                                    window.__inner_intercept = { version: "fusion-1.1" };

                                    // 2.x 通用工具：当前站点 origin + URL 解析
                                    var __INNER_CURRENT_ORIGIN = (function() {
                                        try {
                                            if (window.location.origin) {
                                                return window.location.origin;
                                            }
                                            return window.location.protocol + '//' + window.location.host;
                                        } catch (e) {
                                            return '';
                                        }
                                    })();

                                    function __inner_parse_url(raw) {
                                        try {
                                            var a = document.createElement('a');
                                            a.href = raw;
                                            var origin = a.origin || (a.protocol + '//' + a.host);
                                            return {
                                                href: a.href,
                                                origin: origin || '',
                                                protocol: a.protocol || '',
                                            };
                                        } catch (e) {
                                            return { href: raw || '', origin: '', protocol: '' };
                                        }
                                    }

                                    // 2.0 原始点击日志：无论是否跳转，一律打印一次（方便排查）
                                    document.addEventListener('click', function(e) {
                                        try {
                                            var t = e.target || {};
                                            var tag = t.tagName || '';
                                            var text = (t.innerText || '').slice(0, 30);
                                            var href = '';
                                            // 如果本身是 A 标签或包含 href 属性，取一下
                                            if (t.tagName === 'A') {
                                                href = t.href || t.getAttribute('href') || '';
                                            } else if (t.closest) {
                                                var a = t.closest('a');
                                                if (a) {
                                                    href = a.href || a.getAttribute('href') || '';
                                                    tag = 'A>' + tag;
                                                }
                                            }
                                            if (window.pywebview && window.pywebview.api && window.pywebview.api.log_link_event) {
                                                window.pywebview.api.log_link_event(
                                                    'RAW_CLICK',
                                                    href || window.location.href,
                                                    'button=' + e.button + ',tag=' + tag + ',text=' + text
                                                );
                                            }
                                        } catch (ee) {
                                            console.error('[WebView2] RAW_CLICK 日志上报失败:', ee);
                                        }
                                    }, true);

                                    // 2.1 拦截链接点击（仅左键；右键完全放行）
                                    document.addEventListener('click', function(e) {
                                        // 只处理左键（button=0），右键/中键直接放行
                                        if (e.button !== 0) {
                                            return;
                                        }

                                        try {
                                            var target = e.target;
                                            // 向上查找 A 标签（最多 5 层，避免死循环）
                                            for (var i = 0; i < 5 && target && target !== document; i++) {
                                                if (target.tagName === 'A') {
                                                    var href = target.href || target.getAttribute('href');
                                                    if (href) {
                                                        var info = __inner_parse_url(href);
                                                        var isHttp = /^https?:\\/\\//.test(info.href);
                                                        var isSameOrigin = __INNER_CURRENT_ORIGIN && info.origin && (info.origin === __INNER_CURRENT_ORIGIN);

                                                        // (1) 非 HTTP(S) 且不是 about:，直接拦截（防止调起外部应用）
                                                        if (!isHttp && !/^about:/.test(href)) {
                                                            e.preventDefault();
                                                            e.stopPropagation();
                                                            console.log('[WebView2] 拦截非HTTP链接:', href);
                                                            try {
                                                                if (window.pywebview && window.pywebview.api && window.pywebview.api.log_link_event) {
                                                                    window.pywebview.api.log_link_event(
                                                                        'BLOCK_NON_HTTP_CLICK',
                                                                        href,
                                                                        'target=' + (target.target || '')
                                                                    );
                                                                }
                                                            } catch (ee) {
                                                                console.error('[WebView2] 上报 BLOCK_NON_HTTP_CLICK 失败:', ee);
                                                            }
                                                            return false;
                                                        }
                                                        // (1.5) HTTP(S) 但跨域（外站）链接：一律拦截，防止跳转到外部站点再被系统浏览器接管
                                                        if (isHttp && !isSameOrigin) {
                                                            e.preventDefault();
                                                            e.stopPropagation();
                                                            console.log('[WebView2] 拦截跨域 HTTP 链接(防止外跳):', info.href, 'origin=', info.origin, 'current=', __INNER_CURRENT_ORIGIN);
                                                            try {
                                                                if (window.pywebview && window.pywebview.api && window.pywebview.api.log_link_event) {
                                                                    window.pywebview.api.log_link_event(
                                                                        'BLOCK_EXTERNAL_HTTP_CLICK',
                                                                        info.href,
                                                                        'origin=' + info.origin + ',current=' + __INNER_CURRENT_ORIGIN
                                                                    );
                                                                }
                                                            } catch (ee) {
                                                                console.error('[WebView2] 上报 BLOCK_EXTERNAL_HTTP_CLICK 失败:', ee);
                                                            }
                                                            return false;
                                                        }
                                                        // (2) target=_blank 的 HTTP 链接：在当前窗口打开，防止外置浏览器
                                                        if (target.target === '_blank' && isHttp) {
                                                            e.preventDefault();
                                                            e.stopPropagation();
                                                            console.log('[WebView2] 重定向 _blank 链接到当前窗口:', href);
                                                            try {
                                                                if (window.pywebview && window.pywebview.api && window.pywebview.api.log_link_event) {
                                                                    window.pywebview.api.log_link_event(
                                                                        'REDIRECT_BLANK_TO_INNER',
                                                                        href,
                                                                        'target=_blank'
                                                                    );
                                                                }
                                                            } catch (ee) {
                                                                console.error('[WebView2] 上报 REDIRECT_BLANK_TO_INNER 失败:', ee);
                                                            }
                                                            window.location.href = href;
                                                            return false;
                                                        }
                                                        // (3) 普通 HTTP 链接，直接在当前 WebView 内部导航（记录一下事件，便于调试）
                                                        if (isHttp) {
                                                            try {
                                                                if (window.pywebview && window.pywebview.api && window.pywebview.api.log_link_event) {
                                                                    window.pywebview.api.log_link_event(
                                                                        'INTERNAL_HTTP_CLICK',
                                                                        href,
                                                                        'target=' + (target.target || '')
                                                                    );
                                                                }
                                                            } catch (ee) {
                                                                console.error('[WebView2] 上报 INTERNAL_HTTP_CLICK 失败:', ee);
                                                            }
                                                        }
                                                    }
                                                    break;
                                                }
                                                target = target.parentElement;
                                            }
                                        } catch (err) {
                                            console.error('[WebView2] 链接拦截错误:', err);
                                        }
                                    }, true); // 捕获阶段，优先于站点自己的监听器

                                    // 2.2 拦截 window.open（统一在当前窗口中打开 HTTP 链接），并且周期性“抢回控制权”
                                    try {
                                        // 安全版本的 window.open 实现
                                        window.__inner_safe_open = function(url, name, features) {
                                            try {
                                                var info = __inner_parse_url(url);
                                                var isHttp = /^https?:\\/\\//.test(info.href);
                                                var isSameOrigin = __INNER_CURRENT_ORIGIN && info.origin && (info.origin === __INNER_CURRENT_ORIGIN);

                                                if (url && !isHttp && !/^about:/.test(url)) {
                                                    // 非 HTTP(S) 链接，一律在内置浏览器里拦截，不让系统默认浏览器接管
                                                    console.log('[WebView2] 拦截 window.open 非HTTP 链接:', url);
                                                    try {
                                                        if (window.pywebview && window.pywebview.api && window.pywebview.api.log_link_event) {
                                                            window.pywebview.api.log_link_event(
                                                                'BLOCK_NON_HTTP_WINDOW_OPEN',
                                                                url,
                                                                'name=' + (name || '') + ',features=' + (features || '')
                                                            );
                                                        }
                                                    } catch (ee) {
                                                        console.error('[WebView2] 上报 BLOCK_NON_HTTP_WINDOW_OPEN 失败:', ee);
                                                    }
                                                    return { closed: false, close: function() {} };
                                                }
                                                // HTTP(S) 但跨域：认为是“外站外跳”，直接拦截，防止系统浏览器接管
                                                if (url && isHttp && !isSameOrigin) {
                                                    console.log('[WebView2] 拦截 window.open 跨域 HTTP 链接(防止外跳):', info.href, 'origin=', info.origin, 'current=', __INNER_CURRENT_ORIGIN);
                                                    try {
                                                        if (window.pywebview && window.pywebview.api && window.pywebview.api.log_link_event) {
                                                            window.pywebview.api.log_link_event(
                                                                'BLOCK_EXTERNAL_HTTP_WINDOW_OPEN',
                                                                info.href,
                                                                'origin=' + info.origin + ',current=' + __INNER_CURRENT_ORIGIN
                                                            );
                                                        }
                                                    } catch (ee) {
                                                        console.error('[WebView2] 上报 BLOCK_EXTERNAL_HTTP_WINDOW_OPEN 失败:', ee);
                                                    }
                                                    return { closed: false, close: function() {} };
                                                }
                                                if (url && isHttp) {
                                                    // 所有 HTTP(S) 链接都强制在当前 WebView 内部打开
                                                    console.log('[WebView2] window.open 重定向到当前窗口:', url);
                                                    try {
                                                        if (window.pywebview && window.pywebview.api && window.pywebview.api.log_link_event) {
                                                            window.pywebview.api.log_link_event(
                                                                'WINDOW_OPEN_TO_INNER',
                                                                url,
                                                                'name=' + (name || '') + ',features=' + (features || '')
                                                            );
                                                        }
                                                    } catch (ee) {
                                                        console.error('[WebView2] 上报 WINDOW_OPEN_TO_INNER 失败:', ee);
                                                    }
                                                    window.location.href = url;
                                                    return window;
                                                }
                                            } catch (err) {
                                                console.error('[WebView2] window.open 拦截错误:', err);
                                            }
                                            // 兜底：如果前面都没命中，就让原始 open 来处理
                                            if (window.__inner_original_open) {
                                                return window.__inner_original_open(url, name, features);
                                            }
                                            return null;
                                        };

                                        // 打补丁函数：如果页面试图覆盖 window.open，我们定期抢回
                                        function __patch_window_open() {
                                            try {
                                                if (!window.__inner_original_open) {
                                                    window.__inner_original_open = window.open;
                                                }
                                                if (window.open !== window.__inner_safe_open) {
                                                    window.open = window.__inner_safe_open;
                                                    console.log('[WebView2] 已重新接管 window.open');
                                                }
                                            } catch (e) {
                                                console.error('[WebView2] 抢回 window.open 控制权失败:', e);
                                            }
                                        }

                                        // 立即打一次补丁
                                        __patch_window_open();
                                        // 每 1 秒检查一次，防止站点后续覆盖 window.open
                                        if (!window.__inner_open_patch_timer) {
                                            window.__inner_open_patch_timer = setInterval(__patch_window_open, 1000);
                                        }
                                    } catch (err) {
                                        console.error('[WebView2] 覆盖 window.open 失败:', err);
                                    }

                                    console.log('[WebView2] 融合拦截脚本已注入（防止跳转外置浏览器）');
                                }
                            } catch (e) {
                                console.error('[WebView2] 注入融合拦截脚本失败:', e);
                            }
                        })();
                        """
                        w.evaluate_js(inject_script)
                        print("[WebView2 Runner] [初始化] 已注入关闭前保存Cookie + 融合拦截脚本")
                    except Exception as e:
                        print(f"[WebView2 Runner] [初始化] 注入脚本失败: {e}")
                    
                    return False  # 继续循环
                
                # 智能轮询：定期检查 Cookie 变化（动态调整间隔）
                if current_time - last_save_time[0] >= check_interval[0]:
                    try:
                        print(f"[WebView2 Runner] [智能轮询] 开始检查Cookie（间隔: {check_interval[0]:.1f}秒）")
                        
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
                            print(f"[WebView2 Runner] [智能轮询] 检测到Cookie变化（旧哈希: {last_cookie_hash[0][:8] if last_cookie_hash[0] else 'None'}... -> 新哈希: {current_hash[:8]}...）")
                            saved = cookie_manager.save_cookies_from_webview(w, args.url, verbose=True)
                            if saved:
                                # 只有真的发生变化并写入时才提示（等同"登录/状态更新"场景）
                                print("[WebView2 Runner] [智能轮询] Cookie变化已保存")
                                # 检测到变化后，缩短检查间隔（用户可能还在操作，快速响应）
                                old_interval = check_interval[0]
                                check_interval[0] = 2.0
                                print(f"[WebView2 Runner] [智能轮询] 检查间隔已缩短: {old_interval:.1f}秒 -> {check_interval[0]:.1f}秒")
                            else:
                                # 如果保存失败或内容相同，恢复检查间隔
                                old_interval = check_interval[0]
                                check_interval[0] = 5.0
                                print(f"[WebView2 Runner] [智能轮询] 保存失败，恢复检查间隔: {old_interval:.1f}秒 -> {check_interval[0]:.1f}秒")
                            
                            last_cookie_hash[0] = current_hash
                            last_save_time[0] = current_time
                        elif current_hash is None:
                            # 没有 Cookie，重置哈希
                            if last_cookie_hash[0] is not None:
                                print("[WebView2 Runner] [智能轮询] Cookie已清空，重置状态")
                            last_cookie_hash[0] = None
                            old_interval = check_interval[0]
                            check_interval[0] = 5.0
                            if old_interval != check_interval[0]:
                                print(f"[WebView2 Runner] [智能轮询] 检查间隔已重置: {old_interval:.1f}秒 -> {check_interval[0]:.1f}秒")
                            last_save_time[0] = current_time
                        else:
                            # Cookie 没变化，逐渐延长检查间隔（减少检查频率）
                            old_interval = check_interval[0]
                            check_interval[0] = min(check_interval[0] * 1.5, 30.0)  # 最多延长到30秒
                            if old_interval != check_interval[0]:
                                print(f"[WebView2 Runner] [智能轮询] Cookie无变化，延长检查间隔: {old_interval:.1f}秒 -> {check_interval[0]:.1f}秒")
                            last_save_time[0] = current_time
                    except Exception as e:
                        # 调试：打印错误信息
                        print(f"[WebView2 Runner] [智能轮询] Cookie检查出错: {e}")
                
            except Exception as e:
                print(f"[WebView2 Runner] Cookie操作出错（可忽略）: {e}")

            # 返回 False：继续循环，让窗口一直活着
            return False

        print(f"[WebView2 Runner] 调用 webview.start()...")
        # 启动 Edge 进程监控（仅调试用途，用于大致观察是否有新的 Edge 被拉起）
        start_edge_monitor()
        # 关键：关闭私有模式，否则 pywebview 会使用临时 user data folder（关闭窗口后会清理），导致登录状态无法持久化
        webview.start(
            func=custom_loop,
            args=(window,),
            debug=False,
            user_agent=args.user_agent,
            private_mode=False,
        )
        print(f"[WebView2 Runner] [窗口关闭] webview.start()已返回，窗口已关闭")
        
        # 窗口关闭后的提示（实际的Cookie保存已在beforeunload事件中完成）
        if cookie_saved_on_close[0]:
            print(f"[WebView2 Runner] [窗口关闭] Cookie已在关闭前保存，登录状态已持久化")
        else:
            print(f"[WebView2 Runner] [窗口关闭] 窗口关闭时未检测到Cookie变化（可能用户未登录或未切换账号）")
        
        return 0
    except Exception as e:
        import traceback
        error_msg = f"[WebView2 Runner] 启动失败: {e}\n{traceback.format_exc()}"
        print(error_msg)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


