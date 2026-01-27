"""
工具数据配置
存储所有工具的分类和详细信息
"""

# 工具数据字典
TOOLS_DATA = {
    "热门工具": [
        {"name": "抖音提取作品", "description": "抖音提取作品", "site_key": "douyin", "enabled": True},
        {"name": "快手提取作品", "description": "快手提取作品", "site_key": "kuaishou", "enabled": True},
        {"name": "小红书提取作品", "description": "小红书提取作品", "site_key": "xiaohongshu", "enabled": True},
        {"name": "TK提取作品", "description": "TK提取作品", "enabled": True},
        {"name": "T条提取作品", "description": "T条提取作品", "enabled": True},
        {"name": "BiLi提取作品", "description": "BiLi提取作品", "enabled": True},
        {"name": "YouTube提取作品", "description": "YouTube提取作品", "enabled": True},
    ],
    "作品提取工具": [
        {"name": "抖音提取作品", "description": "抖音提取作品", "site_key": "douyin", "enabled": True},
        {"name": "快手提取作品", "description": "快手提取作品", "site_key": "kuaishou", "enabled": True},
        {"name": "小红书提取作品", "description": "小红书提取作品", "site_key": "xiaohongshu", "enabled": True},
    ],
    "直播录制工具": [
        {"name": "抖音直播录制", "description": "抖音直播录制", "site_key": "douyin", "enabled": True},
        {"name": "快手直播录制", "description": "快手直播录制", "site_key": "kuaishou", "enabled": True},
    ],
    "电商工具": [
        {"name": "抖音电商达人提取", "description": "抖音电商达人提取", "site_key": "douyin", "enabled": True},
    ],
    "AI智能工具": [
        {"name": "AI智能工具1", "description": "AI智能工具1", "enabled": True},
        {"name": "AI智能工具2", "description": "AI智能工具2", "enabled": True},
    ],
    "视音频剪辑工具": [
        {"name": "视频剪辑工具", "description": "视频剪辑工具", "enabled": True},
        {"name": "音频剪辑工具", "description": "音频剪辑工具", "enabled": True},
    ],
    "字幕文案工具": [
        {"name": "字幕工具", "description": "字幕工具", "enabled": True},
        {"name": "文案工具", "description": "文案工具", "enabled": True},
    ],
    "其他工具": [
        {"name": "其他工具1", "description": "其他工具1", "enabled": True},
    ],
    "使用教程问题帮助": [
        {"name": "使用教程", "description": "使用教程", "enabled": True},
        {"name": "问题帮助", "description": "问题帮助", "enabled": True},
    ],
}


def get_tools_by_category(category: str, favorite_tools: set = None) -> list:
    """
    根据分类获取对应的工具列表（只返回启用的工具）
    
    :param category: 工具分类名称
    :param favorite_tools: 收藏的工具名称集合（可选）
    :return: 启用的工具列表
    """
    # 特殊处理"我的收藏工具"分类
    if category == "我的收藏工具":
        if not favorite_tools:
            return []
        # 从所有工具中筛选出收藏的工具，确保每个工具只显示一次
        favorite_tools_list = []
        added_tool_names = set()  # 用于去重，确保每个工具只添加一次
        for cat_tools in TOOLS_DATA.values():
            for tool in cat_tools:
                tool_name = tool["name"]
                # 如果是收藏的工具且还没有添加过，且工具已启用
                if (tool_name in favorite_tools and 
                    tool_name not in added_tool_names and 
                    tool.get("enabled", True)):  # 默认启用
                    favorite_tools_list.append(tool)
                    added_tool_names.add(tool_name)  # 标记为已添加
        return favorite_tools_list
    
    # 获取分类下的工具，过滤掉未启用的工具
    tools = TOOLS_DATA.get(category, [])
    return [tool for tool in tools if tool.get("enabled", True)]  # 默认启用


def get_all_tools() -> list:
    """
    获取所有工具（去重，只返回启用的工具）
    
    :return: 所有启用的工具列表
    """
    all_tools = []
    added_names = set()
    for tools in TOOLS_DATA.values():
        for tool in tools:
            # 只添加启用的工具
            if tool["name"] not in added_names and tool.get("enabled", True):
                all_tools.append(tool)
                added_names.add(tool["name"])
    return all_tools

