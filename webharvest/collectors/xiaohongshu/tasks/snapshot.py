from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class PageSnapshot:
    ts: str
    url: str
    title: str
    cookie_count: int
    user_agent: str


def _outputs_dir() -> Path:
    # webharvest/collectors/xiaohongshu/tasks -> webharvest -> WebHarvest
    root = Path(__file__).resolve().parents[4]
    out = root / "data" / "outputs" / "xiaohongshu"
    out.mkdir(parents=True, exist_ok=True)
    return out


def take_page_snapshot(window: Any, *, user_agent: str = "", save: bool = True) -> Optional[PageSnapshot]:
    """
    最小可用：从当前页面取一些基础信息，便于验证“打开/登录/带 Cookie”链路正常。
    window: pywebview Window（有 evaluate_js 方法）
    """
    try:
        url = window.get_current_url() if hasattr(window, "get_current_url") else ""
    except Exception:
        url = ""

    try:
        title = window.evaluate_js("document.title") or ""
    except Exception:
        title = ""

    try:
        cookie_count = window.evaluate_js(
            """
            (function() {
              try {
                return document.cookie.split(';').map(c => c.trim()).filter(Boolean).length;
              } catch (e) { return 0; }
            })();
            """
        ) or 0
    except Exception:
        cookie_count = 0

    snap = PageSnapshot(
        ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        url=url,
        title=title,
        cookie_count=int(cookie_count),
        user_agent=user_agent,
    )

    if save:
        out = _outputs_dir() / f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        out.write_text(json.dumps(asdict(snap), ensure_ascii=False, indent=2), encoding="utf-8")

    return snap


