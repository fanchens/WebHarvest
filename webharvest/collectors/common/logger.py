from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from .config import ProjectPaths


def get_logger(
    name: str,
    *,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    paths: Optional[ProjectPaths] = None,
) -> logging.Logger:
    """
    获取带文件输出的 logger（按站点/任务拆分时非常有用）
    """
    logger = logging.getLogger(name)
    if getattr(logger, "_webharvest_configured", False):
        return logger

    logger.setLevel(level)
    logger.propagate = False

    fmt = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")

    # console
    sh = logging.StreamHandler()
    sh.setLevel(level)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    # file
    if log_file:
        if paths is None:
            paths = ProjectPaths.detect().ensure()
        log_path = Path(log_file)
        if not log_path.is_absolute():
            log_path = paths.logs_dir / log_file
        log_path.parent.mkdir(parents=True, exist_ok=True)

        fh = RotatingFileHandler(str(log_path), maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    logger._webharvest_configured = True  # type: ignore[attr-defined]
    return logger


