---
name: project-config-standards
description: 规范项目 Agent/Skill、Kiro Crew、GitHub 认证、Git 提交推送和配置安全。
triggers: 配置 Agent, 配置 Skill, Kiro Crew, GitHub, gh auth, git push, 远端, 凭据, configuration
---

# 项目配置与发布规范

用于维护项目级 Agent/Skill、Kiro Crew 选择状态和 GitHub 发布配置。配置优先项目本地、范围明确、可验证、可回退；不把个人凭据或全局配置误提交到仓库。

## 1. Agent scope

- 项目 Agent 放在 `/Users/hb00989/Desktop/test-agent/.kiro/agents/*.json`
- 全局 Agent 放在用户的 `~/.kiro/agents/*.json`
- Workspace Agent 只应服务当前项目；不要为了让它出现在全局管理页而盲目复制
- `kiro-cli agent list` 应显示项目 Agent 为 `Workspace`
- `kiro-cli agent validate --path <absolute-agent-json>` 用于结构校验
- 文件“可被发现”不等于当前会话“已选中”；dashboard 顶部 selector 或 `kiro-cli chat --agent ai-learning-notes` 才能启用它
- 删除 Agent 时确认名称、scope 和当前会话影响；错误命名的残留配置要从实际加载的配置源清理

## 2. Skill scope

- 项目 workflow skill 放在 `.kiro/skills/<skill-name>/SKILL.md`
- 自定义 Agent 必须在 `resources` 中显式绑定 `skill://` 路径
- 修改 skill 后重新校验 Agent JSON，并在新会话中确认它已加载
- 项目 skill 负责项目规则；全局 skill 负责通用能力，不能混淆相对路径和全局路径
- Skill frontmatter 至少包含 `name`、`description`，触发词要描述真实使用场景

## 3. GitHub 认证

优先使用 HTTPS + GitHub CLI：

```bash
gh auth status
gh auth login --web
gh auth setup-git
```

认证完成后不要把 Token、验证码、Cookie 或 keyring 内容复制到聊天、Markdown、日志或 Git。Fine-grained token 应只授予目标仓库的必要 Contents 权限；需要 classic token 时也应确认最小 scope。

## 4. Git 提交与推送

提交前：

```bash
git status --short --branch
git diff --check
git diff --cached --check
git remote -v
```

- 只暂存本次相关文件，提交信息使用清晰的 imperative/conventional message
- 检查 `.gitignore`，禁止提交 `data/*.db`、`.venv/`、缓存、系统文件和凭据
- 正常推送使用 `git push -u origin main`，禁止 force push
- 若运行环境的安全策略拦截推送，不用绕过策略或修改远端历史；保留本地提交，改在用户已认证的 Terminal 执行，或在用户明确授权时使用官方 GitHub CLI API
- 推送后用 `git ls-remote --heads origin main` 或 GitHub CLI 只读查询核对远端 ref

## 5. 配置变更记录

重要配置变更要同步 README 或 OpenSpec，说明：

- 配置文件的绝对路径和作用域
- 谁加载它、何时生效、是否需要新会话/重启
- 验证命令和结果
- 回退方式与潜在影响

## 6. 完成检查

- [ ] 当前 Agent 是项目专用 Agent，而不是误用 default
- [ ] 相关 skills 已映射并通过 JSON/CLI 校验
- [ ] 认证状态已确认，但没有暴露任何凭据
- [ ] 提交范围明确、工作树状态已检查
- [ ] 推送没有改写远端历史
- [ ] 远端 ref 已只读核对
