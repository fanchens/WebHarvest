from __future__ import annotations

from PySide6.QtWidgets import QWidget

from ..browser_login_page import BrowserLoginPage


def create_browser_login_page(*, parent=None, tool_name: str = "", site_key: str = "") -> QWidget:
    return BrowserLoginPage(parent=parent, tool_name=tool_name, site_key=site_key)


