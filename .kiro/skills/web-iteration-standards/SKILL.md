---
name: web-iteration-standards
description: 规范 Gradio 学习笔记网站的代码迭代、CRUD 稳定性、测试和网页验证。
triggers: 修改网站, 更新网页, Gradio, UI, CRUD, 启动项目, 预览页面, web iteration
---

# AI 学习笔记网站迭代规范

用于修改 `/Users/hb00989/Desktop/test-agent` 的 Gradio + SQLite 应用。优先保持可运行、可持久化和可回退，不为了小需求重写已有 CRUD。

## 1. 迭代前

1. 读取相关 OpenSpec proposal/design/spec/tasks 和当前代码。
2. 判断改动属于数据层、章节定义、事件处理、页面布局还是文档/skill。
3. 记录影响范围；若改变需求、数据模型或用户可见行为，补充 README 或 OpenSpec。
4. 不把本地数据库、虚拟环境、缓存和运行日志当作源码修改。

## 2. 不可破坏的行为

- 五个固定章节必须保持：应用层、连接层、交互层、记忆层、基础层
- `data/notes.db` 使用 SQLite，保存完整 CRUD 数据
- 新建、读取、修改、移动章节、删除确认/取消都要保持可用
- 数据库查询使用参数化 SQL，不把用户输入拼接进 SQL
- 修改事件回调时，检查 Gradio outputs 的顺序、State 同步和空状态
- UI 变更不要偷偷改变章节 id、表结构或数据持久化边界

## 3. 实现原则

- 做最小、单一目的改动；避免无关格式化和大范围重构
- 优先复用 `db.py`、`chapters.py` 的现有接口
- 新增逻辑先写清失败路径和输入校验
- 需要迁移数据时提供幂等迁移，不删除用户现有笔记
- 运行中的服务读取的是本地数据库；代码改动后要确认服务是否需要重启

## 4. 验证阶梯

按资源情况从轻到重：

```bash
python3 -m py_compile app.py db.py chapters.py
python3 -m json.tool .kiro/agents/ai-learning-notes.json >/dev/null
python3 -m pip show gradio
curl -fsS http://127.0.0.1:7860/
```

涉及数据库时，至少验证表结构、目标章节和新增/更新记录；涉及 UI 时，验证 HTTP 200、关键文本或可操作路径。不要只凭“进程启动了”宣称 UI 正常。

## 5. 网页预览与证据

启动本地服务并确认监听后，遵守 `web-preview`，发送实际 loopback 地址的 marker。修改用户可见页面或需要确认网页效果时，遵守 `web-verify`：优先使用 `playwright-cli`，其次使用 `agent-browser`；没有浏览器后端时，明确说明只完成了 HTTP/代码验证，不虚构截图。

截图应控制在 2000px 以内，优先一两张能证明改动的画面，不提交截图二进制到仓库。

## 6. 交付前

- [ ] 代码、数据库和界面验证结果分别说明
- [ ] `git diff --check` 通过
- [ ] 只提交源码、文档、OpenSpec 和版本化笔记
- [ ] `data/*.db`、`.venv/`、缓存、日志和凭据未被暂存
- [ ] 若启动了服务，报告地址、端口和停止方式
- [ ] Git 操作不使用 force push、reset --hard 或破坏性清理
