from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    """
    规范化 URL（去掉 fragment，尽量稳定用于去重）
    """
    try:
        p = urlparse(url)
        p = p._replace(fragment="")
        return urlunparse(p)
    except Exception:
        return url


def safe_filename(name: str, *, max_len: int = 120) -> str:
    """
    将任意字符串转成安全文件名（Windows 友好）
    """
    name = name.strip()
    name = re.sub(r"[\\/:*?\"<>|\r\n]+", "_", name)
    if len(name) > max_len:
        name = name[:max_len].rstrip("_")
    return name or "untitled"




