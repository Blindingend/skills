# yx-workflow

`yx-workflow` 是个人 Codex workflow 仓库的总入口。这个仓库用于沉淀可复用的 agent 工作流，例如工作记录、Obsidian 周报素材整理，以及后续可能加入的个人自动化流程。

## 目录结构

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── skills/
│   └── agent-work-tracker/
│       ├── SKILL.md
│       ├── agents/
│       │   └── openai.yaml
│       └── scripts/
│           └── record_work.py
└── tests/
    ├── test_record_work.py
    └── test_skill_layout.py
```

根目录的 `SKILL.md` 是总入口，名称为 `yx-workflow`。具体能力放在 `skills/` 下，由总入口根据任务类型路由到对应子 skill。

## 当前子 Skill

### agent-work-tracker

路径：`skills/agent-work-tracker/`

用途：

- 在较大任务、项目 milestone、实现、排障、部署、CI 修复、调研或计划完成后，记录 agent 工作总结。
- 将原始记录写入 Obsidian：
  `Note/Work/TianYan/AgentTracking/`
- 如果能明确匹配已有项目文档，则追加项目进展：
  `Note/Work/TianYan/项目文档/`
- 在需要生成周报时，作为周报素材来源。

记录脚本：

```bash
python3 /home/yanxin/.codex/skills/yx-workflow/skills/agent-work-tracker/scripts/record_work.py
```

脚本默认执行 Obsidian 仓库同步流程：

1. `git pull --rebase --autostash`
2. 写入 AgentTracking 和匹配到的项目文档
3. `git add` 仅添加本次触碰的文件
4. `git commit -m "docs: 记录 agent 工作进展"`
5. `git pull --rebase --autostash`
6. `git push`

## 安装方式

推荐把整个仓库作为总入口 skill 软链到 Codex skills 目录：

```bash
ln -s /home/yanxin/personal/skills /home/yanxin/.codex/skills/yx-workflow
```

当前预期软链状态：

```text
/home/yanxin/.codex/skills/yx-workflow -> /home/yanxin/personal/skills
```

如果已有同名路径，先确认它指向正确目录，不要覆盖其他已有 skill 软链。

```bash
readlink -f /home/yanxin/.codex/skills/yx-workflow
```

新增或调整 skill 后，通常需要重启 Codex 才能让新的 skill 元数据在后续会话中加载。

## 开发约定

- 新增个人 workflow 时，在 `skills/<skill-name>/` 下创建子 skill。
- 根目录 `SKILL.md` 只做路由，不复制子 skill 的详细流程。
- 子 skill 内保持精简，只放必要的 `SKILL.md`、脚本、引用资料和元数据。
- 不要在单个 skill 目录内添加额外 README；仓库级说明统一维护在根目录 `README.md`。
- 如果子 skill 有脚本，优先为稳定行为补测试。

## 验证

运行单元测试：

```bash
python3 -m unittest discover -s tests -v
```

检查记录脚本语法：

```bash
python3 -m py_compile skills/agent-work-tracker/scripts/record_work.py
```

校验根入口和子 skill：

```bash
python3 /home/yanxin/.codex/skills/.system/skill-creator/scripts/quick_validate.py /home/yanxin/personal/skills
python3 /home/yanxin/.codex/skills/.system/skill-creator/scripts/quick_validate.py /home/yanxin/personal/skills/skills/agent-work-tracker
```
