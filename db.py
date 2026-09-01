"""SQLite persistence layer for AI learning notes.

Single-table schema (see design.md "Data model"):
    notes(id, chapter, title, body, created_at, updated_at)
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import List, Optional

from chapters import CHAPTER_IDS

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "notes.db")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create the data directory and notes table if they don't already exist."""
    os.makedirs(DB_DIR, exist_ok=True)
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter TEXT NOT NULL,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


class ValidationError(Exception):
    """Raised when note input fails validation (e.g. empty title/body)."""


def _validate(chapter: str, title: str, body: str) -> None:
    if chapter not in CHAPTER_IDS:
        raise ValidationError(f"未知章节: {chapter}")
    if not title or not title.strip():
        raise ValidationError("标题不能为空")
    if not body or not body.strip():
        raise ValidationError("内容不能为空")


def create_note(chapter: str, title: str, body: str) -> int:
    """Create a new note. Returns the new note's id. Raises ValidationError on bad input."""
    _validate(chapter, title, body)
    now = _now_iso()
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO notes (chapter, title, body, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (chapter, title.strip(), body.strip(), now, now),
        )
        return cur.lastrowid


def list_notes(chapter: str) -> List[sqlite3.Row]:
    """Return all notes for a chapter, most recently updated first."""
    with _connect() as conn:
        cur = conn.execute(
            "SELECT id, chapter, title, body, created_at, updated_at "
            "FROM notes WHERE chapter = ? ORDER BY updated_at DESC",
            (chapter,),
        )
        return cur.fetchall()


def get_note(note_id: int) -> Optional[sqlite3.Row]:
    """Return a single note by id, or None if it doesn't exist."""
    with _connect() as conn:
        cur = conn.execute(
            "SELECT id, chapter, title, body, created_at, updated_at "
            "FROM notes WHERE id = ?",
            (note_id,),
        )
        return cur.fetchone()


def update_note(note_id: int, chapter: str, title: str, body: str) -> None:
    """Update an existing note's chapter/title/body and bump updated_at."""
    _validate(chapter, title, body)
    now = _now_iso()
    with _connect() as conn:
        conn.execute(
            "UPDATE notes SET chapter = ?, title = ?, body = ?, updated_at = ? "
            "WHERE id = ?",
            (chapter, title.strip(), body.strip(), now, note_id),
        )


def delete_note(note_id: int) -> None:
    """Permanently delete a note by id."""
    with _connect() as conn:
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
