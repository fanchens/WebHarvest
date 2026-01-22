from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional


DEFAULT_UA_POOL: List[str] = [
    # Edge/Chrome 系（Windows）
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    # Edge/Chrome 系（Win11）
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
]


@dataclass
class AntiDetection:
    """
    封控/反检测策略（公共能力）

注意：
- 目前项目使用 pywebview(WebView2)，真正的“请求层 headers/代理”等大多在浏览器/网络层。
- 这里先提供：UA 池、通用 headers、随机节奏（sleep）等通用逻辑，供各站点复用。
    """

    ua_pool: List[str] = None  # type: ignore[assignment]
    min_sleep_s: float = 0.2
    max_sleep_s: float = 1.0

    def __post_init__(self):
        if self.ua_pool is None:
            self.ua_pool = list(DEFAULT_UA_POOL)

    def choose_user_agent(self) -> str:
        return random.choice(self.ua_pool) if self.ua_pool else ""

    def build_headers(self, *, referer: Optional[str] = None) -> Dict[str, str]:
        # 注意：这只是“建议 headers”，是否生效取决于具体实现层（requests/playwright/浏览器注入等）
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1",
        }
        if referer:
            headers["Referer"] = referer
        return headers

    def sleep_jitter(self, *, min_s: Optional[float] = None, max_s: Optional[float] = None):
        """
        随机延迟：模拟用户操作节奏（用于降低风控概率）
        """
        lo = self.min_sleep_s if min_s is None else float(min_s)
        hi = self.max_sleep_s if max_s is None else float(max_s)
        if hi < lo:
            lo, hi = hi, lo
        time.sleep(random.uniform(lo, hi))


