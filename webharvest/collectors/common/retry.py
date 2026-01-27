from __future__ import annotations

import random
import time
from functools import wraps
from collections.abc import Callable
from typing import Type


def retry(
    *,
    max_retries: int = 3,
    base_backoff_s: float = 0.5,
    max_backoff_s: float = 8.0,
    retry_exceptions: tuple[Type[BaseException], ...] = (Exception,),
    on_error: Callable[[BaseException, int], None] | None = None,
):
    """
    通用重试装饰器（指数退避 + 抖动）
    """

    def deco(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except retry_exceptions as e:
                    attempt += 1
                    if on_error:
                        on_error(e, attempt)
                    if attempt > max_retries:
                        raise
                    backoff = min(max_backoff_s, base_backoff_s * (2 ** (attempt - 1)))
                    backoff = backoff * random.uniform(0.7, 1.3)
                    time.sleep(backoff)

        return wrapper

    return deco



