"""
小红书采集任务集合

说明：
- 这里先提供“最小可跑”的任务（抓当前页面信息/保存快照）
- 具体的主页/笔记/搜索等采集，后续按文件扩展
"""

from .snapshot import take_page_snapshot

__all__ = ["take_page_snapshot"]




