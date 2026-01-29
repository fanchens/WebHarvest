from __future__ import annotations

from ._simple_text_page import create_simple_text_page


def create_voice_transcription_page(*, parent=None, tool_name: str = "", site_key: str = ""):
    return create_simple_text_page(
        parent=parent,
        title="语音转写文案",
        description="将语音转换为文字内容。",
    )



