"""
工具窗口右侧页面集合（按菜单项拆分）

约定：
- 每个页面文件提供 create_xxx_page(...) 工厂函数，返回 QWidget
- 工厂函数统一接收（parent, tool_name, site_key），便于按站点差异化
"""

from .works_list_page import create_works_list_page
from .homepage_extract_page import create_homepage_extract_page
from .single_work_extract_page import create_single_work_extract_page
from .keyword_extract_page import create_keyword_extract_page
from .my_homepage_extract_page import create_my_homepage_extract_page
from .universal_browse_extract_page import create_universal_browse_extract_page
from .download_settings_page import create_download_settings_page
from .vip_center_page import create_vip_center_page
from .browser_login_page import create_browser_login_page
from .software_settings_page import create_software_settings_page
from .push_messages_page import create_push_messages_page
from .voice_transcription_page import create_voice_transcription_page
from .tutorial_page import create_tutorial_page

__all__ = [
    "create_works_list_page",
    "create_homepage_extract_page",
    "create_single_work_extract_page",
    "create_keyword_extract_page",
    "create_my_homepage_extract_page",
    "create_universal_browse_extract_page",
    "create_download_settings_page",
    "create_vip_center_page",
    "create_browser_login_page",
    "create_software_settings_page",
    "create_push_messages_page",
    "create_voice_transcription_page",
    "create_tutorial_page",
]


