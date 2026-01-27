"""
Cookie存储管理模块
负责Cookie的持久化存储和读取，支持不同网站分离存储
"""

import json
import time
from pathlib import Path
from datetime import datetime
import hashlib


def _normalize_cookies_for_compare(cookies: list[dict]) -> list[dict]:
    """
    规范化 Cookie 用于对比（避免字段顺序/无关字段导致误判“变化”）
    """
    normalized: list[dict] = []
    for c in cookies or []:
        normalized.append(
            {
                "name": c.get("name", ""),
                "value": c.get("value", ""),
                "domain": c.get("domain", ""),
                "path": c.get("path", "/"),
                "secure": bool(c.get("secure", False)),
                # expires/httponly 等字段在当前采集逻辑里不稳定且常缺失，先不作为判定依据
            }
        )
    normalized.sort(key=lambda x: (x.get("domain", ""), x.get("path", ""), x.get("name", "")))
    return normalized


def _cookies_fingerprint(cookies: list[dict]) -> str:
    payload = json.dumps(_normalize_cookies_for_compare(cookies), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class CookieStorage:
    """Cookie存储管理类"""

    def __init__(self, storage_dir: Path | None = None):
        """
        初始化Cookie存储

        Args:
            storage_dir: 存储目录，默认使用项目data/cookies目录
        """
        if storage_dir is None:
            # 默认存储到项目data目录下（从 browser/ 目录向上3级到项目根目录）
            self.storage_dir = Path(__file__).parent.parent.parent / "data" / "cookies"
        else:
            self.storage_dir = storage_dir

        # 确保目录存在
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_cookies(self, domain: str, cookies: list[dict], *, verbose: bool = True) -> bool:
        """
        保存指定域名的Cookie

        Args:
            domain: 域名，如 'www.baidu.com'
            cookies: Cookie列表，每个Cookie为字典格式

        Returns:
            bool: 保存是否成功
        """
        try:
            file_path = self.storage_dir / f"{domain}.json"

            # 若与当前已保存内容一致，则不写入、不提示（避免“未登录也提示保存”）
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        old_data = json.load(f)
                    old_cookies = old_data.get("cookies", [])
                    if _cookies_fingerprint(old_cookies) == _cookies_fingerprint(cookies):
                        return False
                except Exception:
                    # 读取旧文件失败则继续覆盖写入
                    pass

            data = {
                "domain": domain,
                "cookies": cookies,
                "last_login": datetime.now().isoformat(),
                "login_status": "success",
                "saved_at": datetime.now().isoformat()
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            if verbose:
                print(f"Cookie已保存到: {file_path}")
            return True

        except Exception as e:
            print(f"保存Cookie失败: {e}")
            return False

    def load_cookies(self, domain: str, *, verbose: bool = True) -> list[dict]:
        """
        加载指定域名的Cookie

        Args:
            domain: 域名，如 'www.baidu.com'

        Returns:
            list[dict]: Cookie列表
        """
        try:
            file_path = self.storage_dir / f"{domain}.json"

            if not file_path.exists():
                return []

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            cookies = data.get("cookies", [])
            if verbose:
                print(f"从 {file_path} 加载了 {len(cookies)} 个Cookie")
            return cookies

        except Exception as e:
            print(f"加载Cookie失败: {e}")
            return []

    def has_valid_cookies(self, domain: str) -> bool:
        """
        检查是否有有效的（未过期）Cookie

        Args:
            domain: 域名

        Returns:
            bool: 是否有有效Cookie
        """
        cookies = self.load_cookies(domain)
        if not cookies:
            return False

        current_time = time.time()

        # 检查是否有“看起来还有效”的 Cookie：
        # - 如果带 expires/expirationDate 且大于当前时间 -> 有效
        # - 如果没有任何过期时间字段（典型会话 Cookie） -> 也视为有效
        for cookie in cookies:
            expires = cookie.get("expires", cookie.get("expirationDate"))
            if not expires:
                # 没有过期时间，通常是会话 Cookie，默认认为还有效
                return True
            try:
                if float(expires) > current_time:
                    return True
            except Exception:
                # 非法的 expires 值，保守起见也认为有效，交给站点自己判断
                return True

        return False

    def delete_cookies(self, domain: str) -> bool:
        """
        删除指定域名的Cookie

        Args:
            domain: 域名

        Returns:
            bool: 删除是否成功
        """
        try:
            file_path = self.storage_dir / f"{domain}.json"

            if file_path.exists():
                file_path.unlink()
                print(f"已删除 {domain} 的Cookie文件")
                return True
            else:
                print(f"{domain} 的Cookie文件不存在")
                return False

        except Exception as e:
            print(f"删除Cookie失败: {e}")
            return False

    def list_domains(self) -> list[str]:
        """
        列出所有保存了Cookie的域名

        Returns:
            list[str]: 域名列表
        """
        domains = []
        try:
            for file_path in self.storage_dir.glob("*.json"):
                domain = file_path.stem  # 去掉.json后缀
                domains.append(domain)
        except Exception as e:
            print(f"列出域名失败: {e}")

        return domains

    def get_cookie_info(self, domain: str) -> dict | None:
        """
        获取指定域名的Cookie信息（包括元数据）

        Args:
            domain: 域名

        Returns:
            dict | None: Cookie信息，包含元数据
        """
        try:
            file_path = self.storage_dir / f"{domain}.json"

            if not file_path.exists():
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return data

        except Exception as e:
            print(f"获取Cookie信息失败: {e}")
            return None

    def cleanup_expired_cookies(self) -> int:
        """
        清理所有过期的Cookie文件

        Returns:
            int: 清理的文件数量
        """
        cleaned_count = 0
        current_time = time.time()

        try:
            for file_path in self.storage_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    cookies = data.get("cookies", [])
                    has_valid_cookie = False

                    # 检查是否有有效Cookie
                    for cookie in cookies:
                        expires = cookie.get('expires', cookie.get('expirationDate', 0))
                        if expires > current_time:
                            has_valid_cookie = True
                            break

                    # 如果没有有效Cookie，删除文件
                    if not has_valid_cookie:
                        file_path.unlink()
                        cleaned_count += 1
                        print(f"清理过期Cookie文件: {file_path}")

                except Exception as e:
                    print(f"处理文件 {file_path} 时出错: {e}")

        except Exception as e:
            print(f"清理过期Cookie失败: {e}")

        return cleaned_count

    def export_cookies(self, domain: str, export_path: Path) -> bool:
        """
        导出指定域名的Cookie到文件

        Args:
            domain: 域名
            export_path: 导出文件路径

        Returns:
            bool: 导出是否成功
        """
        try:
            data = self.get_cookie_info(domain)
            if not data:
                print(f"没有找到 {domain} 的Cookie信息")
                return False

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"Cookie已导出到: {export_path}")
            return True

        except Exception as e:
            print(f"导出Cookie失败: {e}")
            return False

    def import_cookies(self, import_path: Path) -> bool:
        """
        从文件导入Cookie

        Args:
            import_path: 导入文件路径

        Returns:
            bool: 导入是否成功
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            domain = data.get("domain")
            cookies = data.get("cookies", [])

            if not domain or not cookies:
                print("导入文件格式错误")
                return False

            return self.save_cookies(domain, cookies)

        except Exception as e:
            print(f"导入Cookie失败: {e}")
            return False

