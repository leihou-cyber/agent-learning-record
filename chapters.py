"""Fixed chapter definitions for the AI learning notes app.

Chapters are intentionally hard-coded (not stored in the database) since
the set is small and fixed by design - see design.md "Data model".
"""

# Each chapter is (id, display_name), ordered as they should appear in the sidebar.
CHAPTERS = [
    ("application", "🎯 应用层 (Agent / Agent Skill)"),
    ("connection", "🔌 连接层 (MCP + Tool / Function Calling)"),
    ("interaction", "💬 交互层 (Prompt: System + User)"),
    ("memory", "🧠 记忆层 (Token + Context + Context Window)"),
    ("foundation", "⚙️ 基础层 (LLM 大语言模型 / Transformer)"),
]

CHAPTER_IDS = [c[0] for c in CHAPTERS]
CHAPTER_NAMES = [c[1] for c in CHAPTERS]
CHAPTER_ID_TO_NAME = dict(CHAPTERS)
CHAPTER_NAME_TO_ID = {name: cid for cid, name in CHAPTERS}


def chapter_name(chapter_id: str) -> str:
    """Return the display name for a chapter id, or the id itself if unknown."""
    return CHAPTER_ID_TO_NAME.get(chapter_id, chapter_id)


def is_valid_chapter(chapter_id: str) -> bool:
    return chapter_id in CHAPTER_ID_TO_NAME
