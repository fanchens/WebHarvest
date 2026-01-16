"""
导航菜单配置
定义左侧导航菜单的项和配置
"""

# 导航项列表（按显示顺序）
NAV_ITEMS = [
    "热门工具",
    "作品提取工具",
    "直播录制工具",
    "电商工具",
    "AI智能工具",
    "视音频剪辑工具",
    "字幕文案工具",
    "其他工具",
    "我的收藏工具",
    "使用教程问题帮助",
]

# 导航项显示控制（True=显示，False=隐藏）
# 如果某个导航项不在这个字典中，默认显示（True）
NAV_ITEMS_VISIBLE = {
    "热门工具": True,
    "作品提取工具": True,
    "直播录制工具": True,
    "电商工具": True,
    "AI智能工具": True,
    "视音频剪辑工具": True,
    "字幕文案工具": True,
    "其他工具": True,
    "我的收藏工具": True,
    "使用教程问题帮助": True,
}


def get_visible_nav_items() -> list:
    """
    获取可见的导航项列表（过滤掉隐藏的导航项）
    
    :return: 可见的导航项列表
    """
    visible_items = []
    for item in NAV_ITEMS:
        # 如果不在配置字典中，默认显示；如果在配置字典中，使用配置的值
        if NAV_ITEMS_VISIBLE.get(item, True):
            visible_items.append(item)
    return visible_items


# 导航项配置（可选，用于扩展）
NAV_ITEM_CONFIG = {
    # 可以在这里添加每个导航项的图标、颜色等配置
    # "热门工具": {
    #     "icon": "...",
    #     "color": "#5a2e8e",
    # },
}

