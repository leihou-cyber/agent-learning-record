## 1. Project Setup

- [x] 1.1 Create project structure (e.g., `app.py`, `db.py`, `data/` directory for the SQLite file)
- [x] 1.2 Add `gradio` as a dependency (requirements.txt or pyproject.toml)
- [x] 1.3 Define the 5 fixed chapters as a constant list (id + display name), matching: 应用层, 连接层, 交互层, 记忆层, 基础层

## 2. Database Layer

- [x] 2.1 Implement SQLite connection/init helper that creates the `notes` table if it doesn't exist (id, chapter, title, body, created_at, updated_at)
- [x] 2.2 Implement `create_note(chapter, title, body)` with input validation (non-empty title/body) and timestamp stamping
- [x] 2.3 Implement `list_notes(chapter)` returning notes for a chapter ordered by `updated_at` descending
- [x] 2.4 Implement `get_note(note_id)` for loading a single note into the editor
- [x] 2.5 Implement `update_note(note_id, chapter, title, body)` that updates `updated_at`
- [x] 2.6 Implement `delete_note(note_id)`

## 3. Sidebar Navigation UI

- [x] 3.1 Build the sidebar component listing all 5 fixed chapters (e.g., `gr.Radio` or button list)
- [x] 3.2 Wire chapter selection to refresh the main panel's note list for the selected chapter
- [x] 3.3 Default to the first chapter selected on initial app load

## 4. Note List & Editor (CRUD UI)

- [x] 4.1 Build the note list view for the selected chapter (title + updated_at), with an empty-state message when there are no notes
- [x] 4.2 Build the note editor form (title textbox, body textbox, chapter dropdown, Save/New/Delete buttons)
- [x] 4.3 Wire "select note from list" to load its content into the editor via `get_note`
- [x] 4.4 Wire "New" button to clear the editor for creating a new note
- [x] 4.5 Wire "Save" button to call `create_note` (new) or `update_note` (existing) depending on editor state, and show validation errors for empty title/body
- [x] 4.6 Wire chapter change + save to move a note between chapters (spec: "Move note to a different chapter")
- [x] 4.7 Wire "Delete" button with a confirm/cancel step before calling `delete_note`
- [x] 4.8 Use `gr.State` to track the currently selected chapter and note id across callbacks

## 5. Wiring & App Entrypoint

- [x] 5.1 Assemble the full `gr.Blocks` layout: sidebar (left) + note list/editor (main content area)
- [x] 5.2 Initialize the SQLite database on app startup
- [x] 5.3 Add `if __name__ == "__main__": demo.launch()` entrypoint

## 6. Verification

- [x] 6.1 Manually verify: create a note in each of the 5 chapters
- [x] 6.2 Manually verify: edit a note's title/body and confirm the update persists
- [x] 6.3 Manually verify: move a note to a different chapter and confirm it appears under the new chapter only
- [x] 6.4 Manually verify: delete a note with confirm, and cancel a delete to confirm it's not removed
- [x] 6.5 Manually verify: restart the app and confirm all notes persisted in SQLite
