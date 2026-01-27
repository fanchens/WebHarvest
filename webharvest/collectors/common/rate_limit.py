from __future__ import annotations

import threading
import time


class RateLimiter:
    """
    极简限流器：按 QPS 做节流（线程安全）
    - acquire() 会阻塞到允许的时间点
    """

    def __init__(self, qps: float):
        self.qps = max(0.0001, float(qps))
        self._min_interval = 1.0 / self.qps
        self._lock = threading.Lock()
        self._next_ts = 0.0

    def acquire(self):
        with self._lock:
            now = time.time()
            if now < self._next_ts:
                time.sleep(self._next_ts - now)
            self._next_ts = time.time() + self._min_interval



