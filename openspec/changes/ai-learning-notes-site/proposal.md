## Why

There is currently no personal tool to record and organize AI learning notes. Learning content about AI systems (agents, MCP, prompts, context, LLM foundations) is scattered and easy to lose track of. A dedicated, structured note-taking site — organized by the layered AI architecture mental model — makes it easy to capture, review, and maintain personal study notes over time.

## What Changes

- Build a new Gradio web application for personal AI learning notes.
- Organize notes into 5 fixed chapters (layers), matching the reference architecture table:
  1. 应用层 (Application Layer) — Agent / Agent Skill
  2. 连接层 (Connection Layer) — MCP + Tool / Function Calling
  3. 交互层 (Interaction Layer) — Prompt (System Prompt + User Prompt)
  4. 记忆层 (Memory Layer) — Token + Context + Context Window
  5. 基础层 (Foundation Layer) — LLM (Transformer Architecture)
- Provide full CRUD (create, read, update, delete) for notes within each chapter.
- Persist notes in a local SQLite database.
- Use a sidebar layout: chapters listed in a left sidebar, note list and editor in the main content area.

## Capabilities

### New Capabilities
- `learning-notes-management`: CRUD operations for learning notes, each note belonging to one of the 5 fixed chapters, backed by SQLite persistence.
- `sidebar-navigation`: Sidebar-based navigation UI for browsing chapters and switching between them to view/manage their notes.

### Modified Capabilities
(none — this is a new project with no existing specs)

## Impact

- New standalone Gradio application (new codebase, no existing app to modify).
- New dependency: `gradio`, Python's built-in `sqlite3` (no extra DB driver needed).
- New local SQLite database file for storing notes.
- No existing APIs, systems, or code are affected since this is a net-new project.
