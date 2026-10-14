"""Application logging setup."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import LOG_DIR


def setup_logging() -> None:
    """Configure rotating file logs for application, testing, and errors."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    def _handler(filename: str, level: int) -> RotatingFileHandler:
        handler = RotatingFileHandler(
            LOG_DIR / filename,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        handler.setLevel(level)
        handler.setFormatter(formatter)
        return handler

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if not any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        root.addHandler(console)

    app_log = logging.getLogger("application")
    app_log.setLevel(logging.INFO)
    if not app_log.handlers:
        app_log.addHandler(_handler("application.log", logging.INFO))
        app_log.propagate = True

    test_log = logging.getLogger("testing")
    test_log.setLevel(logging.INFO)
    if not test_log.handlers:
        test_log.addHandler(_handler("testing.log", logging.INFO))
        test_log.propagate = True

    err_log = logging.getLogger("errors")
    err_log.setLevel(logging.ERROR)
    if not err_log.handlers:
        err_log.addHandler(_handler("errors.log", logging.ERROR))
        err_log.propagate = True
