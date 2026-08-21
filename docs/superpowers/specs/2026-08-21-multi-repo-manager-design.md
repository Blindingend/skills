# Multi-Repo Manager 设计

## 目标

新增个人 skill `multi-repo-manager`，用于管理以 `requirements/` 记录需求、以 `repos/`
submodule 登记参与仓库的跨仓库项目。首批适用仓库是 `scheduler-manager`、`carina` 和
`monitor`。

## 公共模型

父仓库是需求协调和状态记录入口，不承载业务代码：

- 父仓库只在主 checkout 的 `main` 上维护，不创建父仓库分支、worktree 或 MR。
- 每个需求保存在 `requirements/<需求名>/`，优先从仓库自己的
  `requirements/_template/README.md` 创建。
- `repos/` 下的 submodule 只是仓库入口；gitlink 不表示某项需求的实际开发状态。
- `reference` 仓库只读使用 submodule checkout。
- `development` 仓库在 `repos/<仓库名>/.worktree/<需求名>/` 开发，并遵循子仓库自己的
  `AGENTS.md`、分支、验证和交付规则。

## 事实来源

Skill 只保存公共流程。每次使用时先读取当前父仓库和参与子仓库的 `AGENTS.md`、README、
需求模板、现有需求记录和 Git 状态。仓库文档优先于 skill 中的通用默认值；分支名、远端
HEAD、提交、MR、worktree 和发布状态必须现场核对。

## 操作模式

- `bootstrap`：在明确授权下建立或统一父仓库约定和需求模板。
- `audit`：只读检查父仓库、需求记录、submodule 和 worktree 状态。
- `register`：创建需求目录，确定参与仓库角色，fetch 并记录完整基线 SHA。
- `advance`：在子仓库实施或跟踪开发，持续更新提交、MR、验证、阻塞和关键决策。
- `close`：核对最终交付与验证，安全清理 development worktree，保留需求档案。

模式由用户请求决定。只读请求不得创建文件、分支、worktree、提交、MR 或推送。

## 安全边界

- direct-main 只适用于父仓库，不能传播到子仓库。
- “最新”基线必须先 fetch；失败时报告阻塞，不使用可能过期的远端跟踪引用冒充最新状态。
- 不覆盖已有分支或 worktree。
- 清理前逐一检查未提交修改、提交归属和合并状态；未经明确授权不删除分支或 worktree。
- 只暂存本次需求涉及的父仓库文件，保留用户已有脏文件。
- submodule gitlink 只在用户明确要求调整统一入口版本时更新。

## Skill 结构

本次新增：

```text
skills/multi-repo-manager/
├── SKILL.md
└── agents/
    └── openai.yaml
```

同时更新根 `SKILL.md` 路由、根 `README.md` 和布局测试。不增加脚本、内置需求模板或 YAML
状态文件，也不修改三个父仓库；这些仓库的规范统一另行实施。

## 验证

- 在 skill 编写前运行无 skill 的只读压力场景，记录容易遗漏的边界。
- 先增加布局测试并确认因 skill 缺失而失败，再实现最小 skill 使其通过。
- 运行仓库单元测试、skill validator、YAML 解析、字数检查和 `git diff --check`。
- 用压力场景逐项检查 skill 是否覆盖父仓库 direct-main、子仓库隔离、基线、状态记录和安全
  清理。
