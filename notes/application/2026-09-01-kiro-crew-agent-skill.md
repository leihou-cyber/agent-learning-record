# 在 Kiro Crew 中配置项目 Agent 与 Skill

- **所属章节**：应用层
- **记录日期**：2026-09-01

## 一、为什么归入应用层

本项目的五层架构中，应用层明确覆盖 Agent / Agent Skill。Agent 和 Skill 是把模型能力组织成可执行项目工作流的上层配置，不属于基础层的模型原理，也不属于连接层的 MCP 工具通信。

## 二、项目级 Agent 配置

项目专用 Agent 的标准位置是：

`/Users/hb00989/Desktop/test-agent/.kiro/agents/ai-learning-notes.json`

关键配置包括：

- `name`：`ai-learning-notes`
- `model`：`auto`
- `prompt`：说明项目目标、五个固定章节、SQLite 持久化、OpenSpec 和 Git 维护规则
- `tools` / `allowedTools`：文件读写、代码分析、搜索、网页和 Kiro Crew 工具
- `resources`：steering 文件、项目级 OpenSpec skills，以及 `web-preview` / `web-verify`

验证方式：

```bash
cd /Users/hb00989/Desktop/test-agent
kiro-cli agent list
kiro-cli agent validate --path .kiro/agents/ai-learning-notes.json
```

列表中出现 `ai-learning-notes Workspace`，说明当前项目 Agent 已被 Kiro CLI 发现；JSON 校验通过，说明配置结构有效。

## 三、Skill 配置和加载规则

项目级 OpenSpec skills 位于 `.kiro/skills/`，本项目 Agent 绑定了：

- `openspec-apply-change`
- `openspec-archive-change`
- `openspec-explore`
- `openspec-propose`
- `openspec-sync-specs`
- `openspec-update-change`

同时绑定全局网页工作流：

- `web-preview`：本地服务启动并确认可访问后，发出 loopback preview marker
- `web-verify`：对自己修改过的用户界面进行真实浏览器截图验证

Skill 通过 Agent JSON 的 `resources` 字段绑定，例如：

```json
"resources": [
  "file://.kiro/steering/**/*.md",
  "skill://.kiro/skills/openspec-apply-change/SKILL.md",
  "skill://~/.kiro/crew/skills/web-preview/SKILL.md"
]
```

关键经验：自定义 Agent 不会自动继承所有项目工作流。仅创建 Agent 文件只能让它被发现，还需要显式绑定对应的 `skill://` 资源。

## 四、在 Kiro Crew 中真正使用 Agent

Agent 被发现和当前会话选中是两件事：

- Kiro Crew dashboard：在聊天顶部的 agent selector 选择 `ai-learning-notes`
- Kiro CLI：从项目根目录执行 `kiro-cli chat --agent ai-learning-notes`
- 切换 Agent 会创建新的会话上下文，已经启动的 `default` 会话不会自动改名

本次实践中，最初虽然项目里已经有 `ai-learning-notes.json`，但当前会话仍然使用 `default`。直到在 dashboard 中切换并确认当前 Agent 为 `ai-learning-notes` 后，才继续写入本项目经验笔记。这是一个重要的操作顺序：先确认当前会话 Agent 和 Skill 生效，再记录或修改项目内容。

## 五、项目 Agent 与全局 Agent 的 scope 差异

底部 Agent selector 会合并显示当前 workspace 的项目 Agent、全局 Agent 和内置 Agent；Agent 管理页的“已安装代理”主要展示全局 Agent 模板。

因此：

- `ai-learning-notes` 出现在当前项目底部选择器中，说明它是 Workspace Agent
- 它不一定出现在全局 Agent 管理页中，这不是配置失败
- 不应为了让它显示在全局管理页而盲目复制到 `~/.kiro/agents/`，因为它绑定了当前项目的 `.kiro/skills/` 和 steering

另外，历史上错误命名的 `tiaqu-report` 是全局配置残留，已从 Kiro Crew 配置中删除；正确命名的 `taqu-report` 与本项目的 `ai-learning-notes` 保持独立。

## 六、GitHub 推送经验

本地提交和远端推送要区分：

1. 在项目内完成修改和本地 commit
2. 使用 GitHub CLI 完成 HTTPS 认证
3. 再执行 `git push -u origin main`

浏览器认证流程：

```bash
gh auth login --web
gh auth setup-git
gh auth status
cd /Users/hb00989/Desktop/test-agent
git push -u origin main
```

如果终端显示一次性设备码，需要在 `https://github.com/login/device` 完成认证，再回到终端按 Enter 让 CLI 确认结果。不要把 Personal Access Token 粘贴到聊天中。

本次还遇到两个环境边界：Homebrew 镜像队列会拖慢 `gh` 安装；Kiro Crew 主机安全策略可能拦截工具内的 `git push`。因此应区分“GitHub 认证失败”和“当前执行环境禁止推送”，不要用破坏性命令绕过安全策略。

## 七、可复用结论

- 项目 Agent 文件负责“被发现”，会话选择负责“真正生效”
- 自定义 Agent 需要显式绑定项目所需的 Skill
- Agent / Skill 配置变更后必须用 CLI 列表和配置校验做轻量验证
- Workspace Agent 与全局 Agent 的显示位置不同，不能仅凭管理页判断项目 Agent 是否存在
- 本地 SQLite 适合网页运行数据，版本化 Markdown 适合学习经验长期追踪
- Git 推送前先完成 HTTPS 认证，且不要提交 `data/*.db`、虚拟环境、缓存或凭据
