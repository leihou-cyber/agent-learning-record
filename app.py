"""AI Learning Notes - a personal Gradio app for recording AI learning notes,
organized by 5 fixed chapters and persisted in SQLite.

Run with: python app.py
"""

import gradio as gr

import db
from chapters import (
    CHAPTER_ID_TO_NAME,
    CHAPTER_NAME_TO_ID,
    CHAPTER_NAMES,
)

EMPTY_STATE_MSG = "_这个章节还没有笔记，点击“新建笔记”开始记录吧。_"


# ---------------------------------------------------------------------------
# Data helpers (bridge between db.py rows and Gradio-friendly structures)
# ---------------------------------------------------------------------------

def _notes_choices(chapter_id: str):
    """Return (radio_choices, id_by_label) for the notes list of a chapter."""
    rows = db.list_notes(chapter_id)
    choices = []
    id_by_label = {}
    for row in rows:
        label = f"{row['title']}  ·  {row['updated_at']}"
        choices.append(label)
        id_by_label[label] = row["id"]
    return choices, id_by_label


def _render_chapter(chapter_id: str):
    """Build the note-list radio update + empty-state message for a chapter."""
    choices, id_by_label = _notes_choices(chapter_id)
    if choices:
        return (
            gr.update(choices=choices, value=None),
            id_by_label,
            gr.update(value="", visible=False),
        )
    return (
        gr.update(choices=[], value=None),
        id_by_label,
        gr.update(value=EMPTY_STATE_MSG, visible=True),
    )


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

def build_app() -> gr.Blocks:
    default_chapter_name = CHAPTER_NAMES[0]
    default_chapter_id = CHAPTER_NAME_TO_ID[default_chapter_name]

    with gr.Blocks(title="AI 学习笔记") as demo:
        gr.Markdown("# 📚 AI 学习笔记\n个人 AI 学习记录站点，按分层架构整理笔记。")

        # -- State --------------------------------------------------------
        selected_chapter = gr.State(default_chapter_id)
        selected_note_id = gr.State(None)  # None => creating a new note
        note_id_by_label = gr.State({})  # label -> note id, for current chapter

        with gr.Row():
            # -- Sidebar ----------------------------------------------------
            with gr.Column(scale=1, min_width=220):
                gr.Markdown("### 章节")
                chapter_radio = gr.Radio(
                    choices=CHAPTER_NAMES,
                    value=default_chapter_name,
                    label=None,
                    container=False,
                )

            # -- Main content -------------------------------------------------
            with gr.Column(scale=3):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 笔记列表")
                        empty_state = gr.Markdown(value="", visible=False)
                        notes_radio = gr.Radio(choices=[], value=None, label=None, container=False)
                        new_btn = gr.Button("➕ 新建笔记")

                    with gr.Column(scale=2):
                        gr.Markdown("### 笔记编辑")
                        editor_chapter = gr.Dropdown(
                            choices=CHAPTER_NAMES,
                            value=default_chapter_name,
                            label="所属章节",
                        )
                        editor_title = gr.Textbox(label="标题", placeholder="笔记标题")
                        editor_body = gr.Textbox(
                            label="内容", placeholder="记录你学到的内容...", lines=10
                        )
                        status_msg = gr.Markdown(value="")

                        with gr.Row():
                            save_btn = gr.Button("💾 保存", variant="primary")
                            delete_btn = gr.Button("🗑️ 删除", variant="stop")
                            confirm_delete_btn = gr.Button(
                                "⚠️ 确认删除", variant="stop", visible=False
                            )
                            cancel_delete_btn = gr.Button("取消", visible=False)

        # -- Behavior wiring ------------------------------------------------

        def on_chapter_select(chapter_name):
            chapter_id = CHAPTER_NAME_TO_ID[chapter_name]
            notes_update, id_by_label, empty_update = _render_chapter(chapter_id)
            return (
                chapter_id,          # selected_chapter
                None,                # selected_note_id (clear selection)
                id_by_label,         # note_id_by_label
                notes_update,        # notes_radio
                empty_update,        # empty_state
                "",                  # editor_title
                "",                  # editor_body
                chapter_name,        # editor_chapter
                "",                  # status_msg
                gr.update(visible=False),  # confirm_delete_btn
                gr.update(visible=False),  # cancel_delete_btn
            )

        chapter_radio.change(
            on_chapter_select,
            inputs=[chapter_radio],
            outputs=[
                selected_chapter,
                selected_note_id,
                note_id_by_label,
                notes_radio,
                empty_state,
                editor_title,
                editor_body,
                editor_chapter,
                status_msg,
                confirm_delete_btn,
                cancel_delete_btn,
            ],
        )

        def on_select_note(label, id_by_label):
            if not label or label not in id_by_label:
                return gr.update(), gr.update(), gr.update(), None, ""
            note_id = id_by_label[label]
            row = db.get_note(note_id)
            if row is None:
                return gr.update(), gr.update(), gr.update(), None, "笔记不存在，可能已被删除。"
            chapter_name = CHAPTER_ID_TO_NAME[row["chapter"]]
            return row["title"], row["body"], chapter_name, note_id, ""

        notes_radio.change(
            on_select_note,
            inputs=[notes_radio, note_id_by_label],
            outputs=[editor_title, editor_body, editor_chapter, selected_note_id, status_msg],
        )

        def on_new_note(chapter_id):
            chapter_name = CHAPTER_ID_TO_NAME[chapter_id]
            return (
                None,           # selected_note_id -> creating new
                None,           # deselect notes_radio
                "",             # editor_title
                "",             # editor_body
                chapter_name,   # editor_chapter
                "",             # status_msg
                gr.update(visible=False),  # confirm_delete_btn
                gr.update(visible=False),  # cancel_delete_btn
            )

        new_btn.click(
            on_new_note,
            inputs=[selected_chapter],
            outputs=[
                selected_note_id,
                notes_radio,
                editor_title,
                editor_body,
                editor_chapter,
                status_msg,
                confirm_delete_btn,
                cancel_delete_btn,
            ],
        )

        def on_save(note_id, chapter_name, title, body, current_chapter_id):
            target_chapter_id = CHAPTER_NAME_TO_ID[chapter_name]
            try:
                if note_id is None:
                    new_id = db.create_note(target_chapter_id, title, body)
                    msg = "✅ 已创建新笔记。"
                    active_note_id = new_id
                else:
                    db.update_note(note_id, target_chapter_id, title, body)
                    msg = "✅ 已保存修改。"
                    active_note_id = note_id
            except db.ValidationError as e:
                # Refresh the list for the currently displayed chapter, keep editor content
                notes_update, id_by_label, empty_update = _render_chapter(current_chapter_id)
                return (
                    gr.update(),  # selected_note_id unchanged
                    notes_update,
                    id_by_label,
                    empty_update,
                    f"⚠️ {e}",
                    current_chapter_id,
                )

            # After a successful save, refresh the list for the chapter now shown
            # in the sidebar (the note may have moved to a different chapter).
            notes_update, id_by_label, empty_update = _render_chapter(target_chapter_id)
            return (
                active_note_id,
                notes_update,
                id_by_label,
                empty_update,
                msg,
                target_chapter_id,
            )

        save_btn.click(
            on_save,
            inputs=[selected_note_id, editor_chapter, editor_title, editor_body, selected_chapter],
            outputs=[
                selected_note_id,
                notes_radio,
                note_id_by_label,
                empty_state,
                status_msg,
                selected_chapter,
            ],
        )

        # When saving moves a note to a different chapter, keep the sidebar
        # chapter selector in sync with the chapter now being displayed.
        selected_chapter.change(
            lambda chapter_id: CHAPTER_ID_TO_NAME[chapter_id],
            inputs=[selected_chapter],
            outputs=[chapter_radio],
        )

        def on_delete_click(note_id):
            if note_id is None:
                return "", gr.update(visible=False), gr.update(visible=False)
            return (
                "确认要删除这条笔记吗？此操作不可撤销。",
                gr.update(visible=True),
                gr.update(visible=True),
            )

        delete_btn.click(
            on_delete_click,
            inputs=[selected_note_id],
            outputs=[status_msg, confirm_delete_btn, cancel_delete_btn],
        )

        def on_cancel_delete():
            return "", gr.update(visible=False), gr.update(visible=False)

        cancel_delete_btn.click(
            on_cancel_delete,
            outputs=[status_msg, confirm_delete_btn, cancel_delete_btn],
        )

        def on_confirm_delete(note_id, chapter_id):
            if note_id is not None:
                db.delete_note(note_id)
            notes_update, id_by_label, empty_update = _render_chapter(chapter_id)
            return (
                None,          # selected_note_id
                notes_update,  # notes_radio
                id_by_label,   # note_id_by_label
                empty_update,  # empty_state
                "",            # editor_title
                "",            # editor_body
                "🗑️ 笔记已删除。",  # status_msg
                gr.update(visible=False),  # confirm_delete_btn
                gr.update(visible=False),  # cancel_delete_btn
            )

        confirm_delete_btn.click(
            on_confirm_delete,
            inputs=[selected_note_id, selected_chapter],
            outputs=[
                selected_note_id,
                notes_radio,
                note_id_by_label,
                empty_state,
                editor_title,
                editor_body,
                status_msg,
                confirm_delete_btn,
                cancel_delete_btn,
            ],
        )

        # -- Initial load -----------------------------------------------------
        def on_load():
            notes_update, id_by_label, empty_update = _render_chapter(default_chapter_id)
            return notes_update, id_by_label, empty_update

        demo.load(
            on_load,
            outputs=[notes_radio, note_id_by_label, empty_state],
        )

    return demo


if __name__ == "__main__":
    db.init_db()
    app = build_app()
    app.launch()
