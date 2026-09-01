## Context

This is a net-new, single-user, local Gradio application for personal AI learning notes. See proposal.md for motivation. Key constraints from the proposal: 5 fixed chapters, full CRUD, SQLite persistence, sidebar layout.

## Goals / Non-Goals

**Goals:**
- Simple, single-file-friendly Python/Gradio app that can run locally with `python app.py`.
- Sidebar navigation across the 5 fixed chapters with a CRUD-capable main panel.
- Reliable SQLite persistence with minimal setup (no external DB server).

**Non-Goals:**
- Multi-user support, authentication, or access control (single personal user, run locally).
- Rich text / markdown rendering inside notes (plain text body is sufficient for v1).
- Search, tagging, or filtering across chapters (may be considered in a future change).
- Deployment/hosting concerns — this is intended to run locally.

## Decisions

### Tech stack: Gradio Blocks + `sqlite3` (Python standard library)
Using `gr.Blocks` (not `gr.Interface`) because the sidebar + main content layout and CRUD interactions require custom component arrangement and event wiring that `gr.Interface` does not support well.

Using Python's built-in `sqlite3` module rather than an ORM (e.g., SQLAlchemy). Alternatives considered: SQLAlchemy adds abstraction and a dependency that isn't needed for a single-table, single-user app. Raw `sqlite3` with parameterized queries keeps the dependency footprint minimal and the code easy to follow.

### Layout: `gr.Sidebar` (or a narrow `gr.Column`) for chapters + main `gr.Column` for CRUD
Gradio provides layout primitives (`gr.Row`, `gr.Column`, and in recent versions `gr.Sidebar`) that support a persistent left sidebar. The sidebar renders the 5 fixed chapters as a `gr.Radio` or list of buttons; selecting one filters the main panel's note list.

### Data model
Single `notes` table:

| Column      | Type    | Notes                                  |
|-------------|---------|-----------------------------------------|
| id          | INTEGER | PRIMARY KEY AUTOINCREMENT               |
| chapter     | TEXT    | one of 5 fixed chapter keys, NOT NULL   |
| title       | TEXT    | NOT NULL                                |
| body        | TEXT    | NOT NULL                                |
| created_at  | TEXT    | ISO 8601 timestamp, set on insert       |
| updated_at  | TEXT    | ISO 8601 timestamp, set on insert/update|

Chapters are not stored in their own table since the set is fixed and small (5 entries); they are defined as a constant list in code (id + display name), which keeps the schema simple and avoids an unnecessary join. This can be revisited if chapters ever become user-editable.

### Main panel structure
For a selected chapter: a note list (e.g., `gr.Dataframe` or `gr.Radio`/`gr.List`-like selector showing title + updated_at) plus an editor area (title `gr.Textbox`, body `gr.Textbox` multiline, chapter `gr.Dropdown`, Save/Delete/New buttons). Selecting a note from the list loads it into the editor; "New" clears the editor for a fresh note.

### Delete confirmation
Use Gradio's built-in confirmation pattern (a confirm dialog or a two-step "Delete" → "Confirm Delete" button toggle) to satisfy the spec's cancel-delete scenario without adding a modal library dependency.

## Risks / Trade-offs

- [Risk] SQLite file could be accidentally deleted or corrupted, losing all notes → Mitigation: store the `.db` file in a clearly named project data directory (e.g., `data/notes.db`) and document that users should back it up; not automated in v1.
- [Risk] Gradio state management (which note/chapter is selected) across callbacks can get tangled → Mitigation: keep a single source of truth using `gr.State` for "selected chapter" and "selected note id", and re-fetch from SQLite on every relevant callback rather than caching in Python globals.
- [Trade-off] No rich text/markdown rendering keeps the editor simple but limits formatting of learning notes — acceptable for v1 per Non-Goals.

## Open Questions

None — chapter set, storage, CRUD scope, and layout were confirmed with the user before writing this design.
