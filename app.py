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

APP_CSS = """
:root {
    --gh-border: #d0d7de;
    --gh-muted: #656d76;
    --gh-blue: #0969da;
    --gh-bg: #f6f8fa;
}

.gradio-container {
    max-width: 1440px !important;
    padding: 0 !important;
    background: var(--gh-bg) !important;
}

#app-header {
    padding: 22px 28px 18px;
    border-bottom: 1px solid var(--gh-border);
    background: white;
}

#app-header h1 { margin-bottom: 4px; }
#app-header p { color: var(--gh-muted); margin: 0; }
#app-shell { gap: 0 !important; min-height: 720px; }
#chapter-sidebar, #note-list-panel { background: white; border-right: 1px solid var(--gh-border); padding: 20px 16px; }
#chapter-sidebar { min-width: 215px; }
#note-list-panel { min-width: 270px; }
#chapter-sidebar h3, #note-list-panel h3 { margin-top: 0; }
#chapter-sidebar .gr-radio, #note-list-panel .gr-radio { border: 0; box-shadow: none; }
#chapter-sidebar label span { font-size: 14px; }
#chapter-sidebar input:checked + span { color: var(--gh-blue); font-weight: 650; }
#editor-panel { padding: 24px 34px 42px; background: white; }
#editor-drawer { margin-top: 18px; border: 1px solid var(--gh-border); border-radius: 8px; background: white; }
#editor-drawer .label-wrap { color: #1f2328; font-weight: 650; }
#editor-drawer .label-wrap:hover { color: var(--gh-blue); }
#editor-panel .gr-tabs { border: 0; }
#editor-panel .tab-nav { border-bottom: 1px solid var(--gh-border); }
#editor-panel .tab-nav button { border: 0; border-bottom: 2px solid transparent; border-radius: 0; color: var(--gh-muted); }
#editor-panel .tab-nav button.selected { border-bottom-color: var(--gh-blue); color: #1f2328; font-weight: 650; }
#preview-body { padding: 10px 4px 26px; min-height: 430px; }
#preview-body h1, #preview-body h2, #preview-body h3 { border-bottom: 1px solid var(--gh-border); padding-bottom: 8px; }
#preview-body code { background: #f6f8fa; border: 1px solid #d8dee4; border-radius: 5px; padding: 2px 5px; }
#editor-body textarea { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important; line-height: 1.55 !important; }
#status-msg { min-height: 26px; color: var(--gh-muted); }
@media (max-width: 900px) {
    #app-shell { flex-wrap: wrap; }
    #chapter-sidebar { min-width: 180px; }
    #note-list-panel { min-width: 230px; }
    #editor-panel { min-width: 100%; }
}
"""


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

PREVIEW_EMPTY_MSG = "_在左侧选择一篇笔记，或点击“新建笔记”开始编辑。_"


def _markdown_preview(body: str):
    """Return the current Markdown body for the Preview tab."""
    return body.strip() if body and body.strip() else PREVIEW_EMPTY_MSG


def build_app() -> gr.Blocks:
    default_chapter_name = CHAPTER_NAMES[0]
    default_chapter_id = CHAPTER_NAME_TO_ID[default_chapter_name]

    with gr.Blocks(css=APP_CSS, title="AI 学习笔记") as demo:
        gr.Markdown(
            "# 📚 AI 学习笔记\n个人 AI 学习记录站点，按分层架构整理笔记。",
            elem_id="app-header",
        )

        # -- State --------------------------------------------------------
        selected_chapter = gr.State(default_chapter_id)
        selected_note_id = gr.State(None)  # None => creating a new note
        note_id_by_label = gr.State({})  # label -> note id, for current chapter

        with gr.Row(elem_id="app-shell"):
            # -- Fixed chapter sidebar -------------------------------------
            with gr.Column(scale=1, min_width=215, elem_id="chapter-sidebar"):
                gr.Markdown("### 章节")
                chapter_radio = gr.Radio(
                    choices=CHAPTER_NAMES,
                    value=default_chapter_name,
                    label=None,
                    container=False,
                )

            # -- Note list --------------------------------------------------
            with gr.Column(scale=1, min_width=270, elem_id="note-list-panel"):
                gr.Markdown("### 笔记列表")
                empty_state = gr.Markdown(value="", visible=False)
                notes_radio = gr.Radio(choices=[], value=None, label=None, container=False)
                new_btn = gr.Button("➕ 新建笔记")

            # -- GitHub-style document editor ------------------------------
            with gr.Column(scale=3, min_width=520, elem_id="editor-panel"):
                with gr.Accordion(
                    "✏️ 编辑标题和章节", open=False, elem_id="editor-drawer"
                ):
                    editor_chapter = gr.Dropdown(
                        choices=CHAPTER_NAMES,
                        value=default_chapter_name,
                        label="所属章节",
                    )
                    editor_title = gr.Textbox(label="标题", placeholder="笔记标题")

                with gr.Tabs():
                    with gr.Tab("Preview"):
                        preview_body = gr.Markdown(
                            value=PREVIEW_EMPTY_MSG,
                            elem_id="preview-body",
                        )
                    with gr.Tab("Code"):
                        editor_body = gr.Textbox(
                            label="Markdown 原文",
                            placeholder="记录你学到的内容...",
                            lines=20,
                            elem_id="editor-body",
                        )
                status_msg = gr.Markdown(
                    value="自动保存：标题或正文失焦后写入 SQLite。",
                    elem_id="status-msg",
                )

                with gr.Row():
                    save_btn = gr.Button("💾 立即保存", variant="primary")
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
                PREVIEW_EMPTY_MSG,   # preview_body
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
                preview_body,
                editor_chapter,
                status_msg,
                confirm_delete_btn,
                cancel_delete_btn,
            ],
        )

        def on_select_note(label, id_by_label):
            if not label or label not in id_by_label:
                return gr.update(), gr.update(), gr.update(), gr.update(), None, ""
            note_id = id_by_label[label]
            row = db.get_note(note_id)
            if row is None:
                return gr.update(), gr.update(), gr.update(), gr.update(), None, "笔记不存在，可能已被删除。"
            chapter_name = CHAPTER_ID_TO_NAME[row["chapter"]]
            return row["title"], row["body"], _markdown_preview(row["body"]), chapter_name, note_id, ""

        notes_radio.change(
            on_select_note,
            inputs=[notes_radio, note_id_by_label],
            outputs=[
                editor_title,
                editor_body,
                preview_body,
                editor_chapter,
                selected_note_id,
                status_msg,
            ],
        )

        def on_new_note(chapter_id):
            chapter_name = CHAPTER_ID_TO_NAME[chapter_id]
            return (
                None,           # selected_note_id -> creating new
                None,           # deselect notes_radio
                "",             # editor_title
                "",             # editor_body
                PREVIEW_EMPTY_MSG,  # preview_body
                chapter_name,   # editor_chapter
                "准备新建笔记：填写标题和正文后，失焦会自动保存。",  # status_msg
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
                preview_body,
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
                    _markdown_preview(body),
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
                _markdown_preview(body),
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
                preview_body,
                status_msg,
                selected_chapter,
            ],
        )

        def on_body_input(body):
            return _markdown_preview(body), "✎ 草稿已更新；切换焦点后会自动保存。"

        editor_body.input(
            on_body_input,
            inputs=[editor_body],
            outputs=[preview_body, status_msg],
        )

        def on_auto_save(note_id, chapter_name, title, body, current_chapter_id):
            if not title or not title.strip() or not body or not body.strip():
                return (
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    _markdown_preview(body),
                    "草稿已保留；标题和正文都填写后，失焦会自动保存。",
                    current_chapter_id,
                )
            return on_save(note_id, chapter_name, title, body, current_chapter_id)

        for component in (editor_title, editor_body):
            component.change(
                on_auto_save,
                inputs=[selected_note_id, editor_chapter, editor_title, editor_body, selected_chapter],
                outputs=[
                    selected_note_id,
                    notes_radio,
                    note_id_by_label,
                    empty_state,
                    preview_body,
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
                PREVIEW_EMPTY_MSG,  # preview_body
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
                preview_body,
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
