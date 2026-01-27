"""
按站点管理工具窗口左侧菜单 / 页面配置

设计目标：
- 不再在代码里写死“这一套固定菜单”，而是按站点（抖音/快手/小红书…）配置
- 方便后续：
  - 不同站点用不同菜单
  - 给每个菜单项挂载不同的“页面类型”或页面类
"""

from __future__ import annotations

from typing import Callable, TypedDict

from PySide6.QtWidgets import QWidget

from .pages import (
    create_works_list_page,
    create_homepage_extract_page,
    create_single_work_extract_page,
    create_keyword_extract_page,
    create_my_homepage_extract_page,
    create_universal_browse_extract_page,
    create_download_settings_page,
    create_vip_center_page,
    create_browser_login_page,
    create_software_settings_page,
    create_push_messages_page,
    create_voice_transcription_page,
    create_tutorial_page,
)


class MenuItemConfig(TypedDict, total=False):
    """单个菜单项配置"""

    key: str          # 内部标识（可选，暂时主要用中文标题做 key）
    title: str        # 左侧显示的标题（例如：作品列表）
    page_type: str    # 右侧页面类型：works_list / homepage / single_work / keyword / browser_login / text ...
    visible: bool     # 是否在左侧菜单显示（隐藏但不删除页面）


class SiteProfile(TypedDict):
    """站点配置：左侧菜单 + 页面类型映射"""

    site_key: str
    menu_items: list[MenuItemConfig]
    page_factories: dict[str, Callable[..., QWidget]]


def _default_page_factories() -> dict[str, Callable[..., QWidget]]:
    """
    page_type -> 工厂函数
    工厂函数签名约定：create_xxx_page(parent=None, tool_name="", site_key="") -> QWidget
    """
    return {
        "works_list": create_works_list_page,
        "homepage": create_homepage_extract_page,
        "single_work": create_single_work_extract_page,
        "keyword": create_keyword_extract_page,
        "my_homepage": create_my_homepage_extract_page,
        "universal_browse": create_universal_browse_extract_page,
        "download_settings": create_download_settings_page,
        "vip_center": create_vip_center_page,
        "browser_login": create_browser_login_page,
        "software_settings": create_software_settings_page,
        "push_messages": create_push_messages_page,
        "voice_transcription": create_voice_transcription_page,
        "tutorial": create_tutorial_page,
    }


# 按站点配置菜单：风格类似 tools_config.TOOLS_DATA，直观可读
SITE_PROFILES: dict[str, SiteProfile] = {
    "douyin": SiteProfile(
        site_key="douyin",
        menu_items=[
            MenuItemConfig(title="作品列表",     key="works_list",          page_type="works_list",          visible=True),
            MenuItemConfig(title="主页提取",     key="homepage",            page_type="homepage",            visible=True),
            MenuItemConfig(title="单作品提取",   key="single_work",         page_type="single_work",         visible=True),
            MenuItemConfig(title="关键词提取",   key="keyword",             page_type="keyword",             visible=True),
            MenuItemConfig(title="我的主页提取", key="my_homepage",         page_type="my_homepage",         visible=True),
            MenuItemConfig(title="万能浏览提取", key="universal_browse",    page_type="universal_browse",    visible=True),
            MenuItemConfig(title="下载设置",     key="download_settings",   page_type="download_settings",   visible=True),
            MenuItemConfig(title="VIP中心",      key="vip_center",          page_type="vip_center",          visible=True),
            MenuItemConfig(title="浏览器 登录",  key="browser_login",       page_type="browser_login",       visible=True),
            MenuItemConfig(title="软件设置",     key="software_settings",   page_type="software_settings",   visible=True),
            MenuItemConfig(title="推送消息",     key="push_messages",       page_type="push_messages",       visible=True),
            MenuItemConfig(title="语音转写文案", key="voice_transcription", page_type="voice_transcription", visible=True),
            MenuItemConfig(title="使用教程",     key="tutorial",            page_type="tutorial",            visible=True),
        ],
        page_factories=_default_page_factories(),
    ),
    "kuaishou": SiteProfile(
        site_key="kuaishou",
        # 快手：语音转写文案 先隐藏（页面保留，后续可随时改 visible=True）
        menu_items=[
            MenuItemConfig(title="作品列表",     key="works_list",          page_type="works_list",          visible=True),
            MenuItemConfig(title="主页提取",     key="homepage",            page_type="homepage",            visible=True),
            MenuItemConfig(title="单作品提取",   key="single_work",         page_type="single_work",         visible=True),
            MenuItemConfig(title="关键词提取",   key="keyword",             page_type="keyword",             visible=True),
            MenuItemConfig(title="我的主页提取", key="my_homepage",         page_type="my_homepage",         visible=True),
            MenuItemConfig(title="万能浏览提取", key="universal_browse",    page_type="universal_browse",    visible=True),
            MenuItemConfig(title="下载设置",     key="download_settings",   page_type="download_settings",   visible=True),
            MenuItemConfig(title="VIP中心",      key="vip_center",          page_type="vip_center",          visible=True),
            MenuItemConfig(title="浏览器 登录",  key="browser_login",       page_type="browser_login",       visible=True),
            MenuItemConfig(title="软件设置",     key="software_settings",   page_type="software_settings",   visible=True),
            MenuItemConfig(title="推送消息",     key="push_messages",       page_type="push_messages",       visible=True),
            MenuItemConfig(title="语音转写文案", key="voice_transcription", page_type="voice_transcription", visible=False),
            MenuItemConfig(title="使用教程",     key="tutorial",            page_type="tutorial",            visible=True),
        ],
        page_factories=_default_page_factories(),
    ),
    "xiaohongshu": SiteProfile(
        site_key="xiaohongshu",
        # 小红书：语音转写文案 先隐藏（页面保留，后续可随时改 visible=True）
        menu_items=[
            MenuItemConfig(title="作品列表",     key="works_list",          page_type="works_list",          visible=True),
            MenuItemConfig(title="主页提取",     key="homepage",            page_type="homepage",            visible=True),
            MenuItemConfig(title="单作品提取",   key="single_work",         page_type="single_work",         visible=True),
            MenuItemConfig(title="关键词提取",   key="keyword",             page_type="keyword",             visible=True),
            MenuItemConfig(title="我的主页提取", key="my_homepage",         page_type="my_homepage",         visible=True),
            MenuItemConfig(title="万能浏览提取", key="universal_browse",    page_type="universal_browse",    visible=True),
            MenuItemConfig(title="下载设置",     key="download_settings",   page_type="download_settings",   visible=True),
            MenuItemConfig(title="VIP中心",      key="vip_center",          page_type="vip_center",          visible=True),
            MenuItemConfig(title="浏览器 登录",  key="browser_login",       page_type="browser_login",       visible=True),
            MenuItemConfig(title="软件设置",     key="software_settings",   page_type="software_settings",   visible=True),
            MenuItemConfig(title="推送消息",     key="push_messages",       page_type="push_messages",       visible=True),
            MenuItemConfig(title="语音转写文案", key="voice_transcription", page_type="voice_transcription", visible=False),
            MenuItemConfig(title="使用教程",     key="tutorial",            page_type="tutorial",            visible=True),
        ],
        page_factories=_default_page_factories(),
    ),
    # 兜底：其它站点或未指定站点时使用
    "default": SiteProfile(
        site_key="default",
        menu_items=[
            MenuItemConfig(title="作品列表",     key="works_list",          page_type="works_list",          visible=True),
            MenuItemConfig(title="主页提取",     key="homepage",            page_type="homepage",            visible=True),
            MenuItemConfig(title="单作品提取",   key="single_work",         page_type="single_work",         visible=True),
            MenuItemConfig(title="关键词提取",   key="keyword",             page_type="keyword",             visible=True),
            MenuItemConfig(title="我的主页提取", key="my_homepage",         page_type="my_homepage",         visible=True),
            MenuItemConfig(title="万能浏览提取", key="universal_browse",    page_type="universal_browse",    visible=True),
            MenuItemConfig(title="下载设置",     key="download_settings",   page_type="download_settings",   visible=True),
            MenuItemConfig(title="VIP中心",      key="vip_center",          page_type="vip_center",          visible=True),
            MenuItemConfig(title="浏览器 登录",  key="browser_login",       page_type="browser_login",       visible=True),
            MenuItemConfig(title="软件设置",     key="software_settings",   page_type="software_settings",   visible=True),
            MenuItemConfig(title="推送消息",     key="push_messages",       page_type="push_messages",       visible=True),
            MenuItemConfig(title="语音转写文案", key="voice_transcription", page_type="voice_transcription", visible=True),
            MenuItemConfig(title="使用教程",     key="tutorial",            page_type="tutorial",            visible=True),
        ],
        page_factories=_default_page_factories(),
    ),
}


def get_site_profile(site_key: str | None) -> SiteProfile:
    """
    获取站点配置：
    - 传入 douyin / kuaishou / xiaohongshu 时返回对应配置
    - 其它情况统一回退到 default
    """
    key = (site_key or "").lower()
    if key in SITE_PROFILES:
        return SITE_PROFILES[key]
    return SITE_PROFILES["default"]


