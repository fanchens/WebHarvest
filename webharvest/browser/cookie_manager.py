"""
Cookie管理模块
负责Cookie的获取、应用和管理，支持 WebView2
"""

import time
import json
from urllib.parse import urlparse

from .cookie_storage import CookieStorage


class CookieManager:
    """Cookie管理器 - 适配 WebView2"""

    def __init__(self):
        self.cookie_storage = CookieStorage()

    def extract_domain_from_url(self, url: str) -> str:
        """
        从URL中提取域名

        Args:
            url: 完整的URL

        Returns:
            str: 域名，如 'www.baidu.com'
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc

            # 移除端口号
            if ':' in domain:
                domain = domain.split(':')[0]

            return domain
        except Exception as e:
            print(f"提取域名失败: {e}")
            return ""

    def save_cookies_from_webview(self, webview_window, url: str, *, verbose: bool = True) -> bool:
        """
        从 WebView2 中保存Cookie

        Args:
            webview_window: WebView2 窗口实例
            url: 当前页面的URL

        Returns:
            bool: 保存是否成功
        """
        try:
            domain = self.extract_domain_from_url(url)
            if not domain:
                print("无法提取域名，取消保存Cookie")
                return False

            # 通过 JavaScript 获取所有 Cookie
            script = """
            (function() {
                var cookies = document.cookie.split(';').map(function(c) {
                    var parts = c.trim().split('=');
                    if (parts.length === 2) {
                        return {
                            name: parts[0],
                            value: parts[1],
                            domain: window.location.hostname,
                            path: '/',
                            secure: window.location.protocol === 'https:',
                            httpOnly: false
                        };
                    }
                    return null;
                }).filter(function(c) { return c !== null; });
                return JSON.stringify(cookies);
            })();
            """

            try:
                cookies_json = webview_window.evaluate_js(script)
                if not cookies_json:
                    # 没有 Cookie 也正常（用户可能未登录），静默返回
                    return False

                cookies = json.loads(cookies_json)
                if not cookies:
                    # 没有 Cookie 也正常（用户可能未登录），静默返回
                    return False

                # 过滤出属于当前域名的Cookie
                domain_cookies = [
                    cookie for cookie in cookies
                    if domain in cookie.get("domain", "")
                ]

                if verbose:
                    print(f"[CookieManager] URL={url} 域名={domain} 抓到 Cookie 总数={len(cookies)}，匹配当前域名的={len(domain_cookies)}")

                if domain_cookies:
                    success = self.cookie_storage.save_cookies(domain, domain_cookies, verbose=verbose)
                    if success and verbose:
                        print(f"✓ 已保存 {len(domain_cookies)} 个Cookie到 {domain}")
                    return success
                else:
                    # 没有 Cookie 也正常（用户可能未登录），静默返回
                    return False

            except Exception as e:
                # 获取 Cookie 失败也静默处理（可能是页面未加载完成）
                return False

        except Exception as e:
            print(f"保存浏览器Cookie失败: {e}")
            return False

    def apply_cookies_to_webview(self, webview_window, url: str, *, verbose: bool = False) -> bool:
        """
        应用已保存的Cookie到 WebView2（静默模式，不打印错误）

        Args:
            webview_window: WebView2 窗口实例
            url: 目标页面的URL

        Returns:
            bool: 应用是否成功
        """
        try:
            domain = self.extract_domain_from_url(url)
            if not domain:
                return False  # 静默返回，不打印错误

            # 检查是否有有效的Cookie（静默检查）
            if not self.cookie_storage.has_valid_cookies(domain):
                return False  # 没有 Cookie 也正常，静默返回

            # 加载Cookie
            cookies = self.cookie_storage.load_cookies(domain, verbose=verbose)
            if not cookies:
                return False  # 没有 Cookie 也正常，静默返回

            # 通过 JavaScript 设置 Cookie
            cookie_scripts = []
            for cookie in cookies:
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                cookie_domain = cookie.get('domain', domain)
                path = cookie.get('path', '/')
                secure = cookie.get('secure', False)

                # 构建 Cookie 字符串
                cookie_str = f"{name}={value}; path={path}"
                if cookie_domain:
                    cookie_str += f"; domain={cookie_domain}"
                if secure:
                    cookie_str += "; secure"

                cookie_scripts.append(f"document.cookie = '{cookie_str}';")

            # 执行所有 Cookie 设置脚本
            script = " ".join(cookie_scripts)
            try:
                webview_window.evaluate_js(script)
                if verbose:
                    print(f"✓ 已自动加载 {len(cookies)} 个Cookie，实现自动登录")
                return True
            except Exception as e:
                return False  # 静默处理错误

        except Exception as e:
            return False  # 静默处理错误

    def has_valid_login(self, url: str) -> bool:
        """
        检查指定URL是否有有效的登录状态

        Args:
            url: 页面URL

        Returns:
            bool: 是否已登录
        """
        domain = self.extract_domain_from_url(url)
        return self.cookie_storage.has_valid_cookies(domain)

    def delete_login_info(self, url: str) -> bool:
        """
        删除指定URL的登录信息

        Args:
            url: 页面URL

        Returns:
            bool: 删除是否成功
        """
        domain = self.extract_domain_from_url(url)
        return self.cookie_storage.delete_cookies(domain)

    def get_login_status(self, url: str) -> dict:
        """
        获取登录状态信息

        Args:
            url: 页面URL

        Returns:
            dict: 登录状态信息
        """
        domain = self.extract_domain_from_url(url)
        cookie_info = self.cookie_storage.get_cookie_info(domain)

        if cookie_info:
            return {
                'domain': domain,
                'has_cookies': True,
                'cookie_count': len(cookie_info.get('cookies', [])),
                'last_login': cookie_info.get('last_login'),
                'login_status': cookie_info.get('login_status')
            }
        else:
            return {
                'domain': domain,
                'has_cookies': False,
                'cookie_count': 0,
                'last_login': None,
                'login_status': 'not_logged_in'
            }

