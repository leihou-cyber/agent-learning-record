# AI 学习笔记记录

一个用于记录和整理 AI 学习内容的本地 Gradio 应用。笔记按 AI 分层架构组织为五个固定章节：应用层、连接层、交互层、记忆层和基础层。

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

启动后访问 Gradio 输出的本地地址即可使用。数据保存在 `data/notes.db`，该文件只存在于本地并被 Git 忽略；如需迁移或备份，请单独保存数据库文件。

## 项目结构

- `app.py`：Gradio 界面和事件处理
- `db.py`：SQLite 初始化及笔记 CRUD
- `chapters.py`：五个固定章节定义
- `data/`：本地 SQLite 数据目录
- `openspec/`：需求、设计和实现任务记录
- `.kiro/agents/ai-learning-notes.json`：Kiro Crew 项目级 agent 配置

## Kiro Crew agent

本项目包含名为 `ai-learning-notes` 的项目级 agent。Kiro Crew/Kiro CLI 在当前项目目录下会优先发现 `.kiro/agents/*.json`，可在 agent 选择器中选择 `ai-learning-notes`，用于后续实验、开发和维护。

### Agent 与 Skill 配置

- 用 `kiro-cli agent list` 确认列表中出现 `ai-learning-notes (Workspace)`。
- Kiro Crew dashboard：在聊天顶部的 agent selector 中选择 `ai-learning-notes`；切换 agent 会创建新的会话上下文，当前已经启动的 default 会话不会自动改名。
- Kiro CLI：从项目根目录使用 `kiro-cli chat --agent ai-learning-notes` 启动指定 agent。
- agent 已绑定项目级 OpenSpec skills，以及全局 `web-preview` 和 `web-verify` skills；配置位于 `.kiro/agents/ai-learning-notes.json` 的 `resources` 字段。
- 重要规则：项目 agent 文件“可被发现”不等于“当前会话已选中”，必须在新会话启动时选择或传入 `ai-learning-notes`。

## 维护约定

- 代码改动后运行 `python3 -m py_compile app.py db.py chapters.py`。
- 新功能先在 `openspec/changes/` 中记录需求和任务，再实现代码。
- 不提交本地数据库、虚拟环境、缓存和系统生成文件。
