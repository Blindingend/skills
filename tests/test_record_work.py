import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "agent-work-tracker"
    / "scripts"
    / "record_work.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("record_work", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeGit:
    def __init__(self, dirty_output=""):
        self.commands = []
        self.dirty_output = dirty_output

    def run(self, repo, args, check=True, capture_output=False):
        self.commands.append(list(args))
        if args[:1] == ["status"]:
            return subprocess.CompletedProcess(args, 0, self.dirty_output, "")
        if args[:1] == ["diff"]:
            return subprocess.CompletedProcess(args, 1, "", "")
        return subprocess.CompletedProcess(args, 0, "", "")


class RecordWorkTests(unittest.TestCase):
    def test_week_ending_friday_uses_current_or_next_friday(self):
        module = load_module()

        self.assertEqual(module.week_ending_friday(date(2026, 5, 18)), date(2026, 5, 22))
        self.assertEqual(module.week_ending_friday(date(2026, 5, 22)), date(2026, 5, 22))
        self.assertEqual(module.week_ending_friday(date(2026, 5, 23)), date(2026, 5, 29))

    def test_append_tracking_entry_creates_week_file_and_appends_entries(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tracking_file = Path(tmp) / "2026-05-22 Agent Tracking.md"
            record = module.WorkRecord.from_mapping(
                {
                    "title": "实现 Agent 工作追踪 skill",
                    "status": "completed",
                    "repo": "/home/yanxin/personal/skills",
                    "project": "AgentTracking",
                    "summary": "创建记录脚本和 skill 指令。",
                    "outputs": ["agent-work-tracker/SKILL.md"],
                    "verification": ["python -m unittest"],
                    "next_steps": ["重启 Codex 加载 skill"],
                }
            )

            module.append_tracking_entry(
                tracking_file,
                record,
                recorded_at="2026-05-22 18:30",
                week_end=date(2026, 5, 22),
            )
            module.append_tracking_entry(
                tracking_file,
                record,
                recorded_at="2026-05-22 18:45",
                week_end=date(2026, 5, 22),
            )

            content = tracking_file.read_text(encoding="utf-8")
            self.assertIn("# 2026-05-22 Agent Tracking", content)
            self.assertEqual(content.count("### 2026-05-22 18:"), 2)
            self.assertIn("**项目**：AgentTracking", content)
            self.assertIn("- agent-work-tracker/SKILL.md", content)

    def test_project_doc_matching_updates_only_single_existing_match(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            scheduler_doc = project_dir / "Scheduler 推进.md"
            scheduler_doc.write_text("# Scheduler 推进\n", encoding="utf-8")
            (project_dir / "scheduler replay.md").write_text("# Other\n", encoding="utf-8")
            market_doc = project_dir / "Market Compare 行情对比.md"
            market_doc.write_text("# Market Compare\n", encoding="utf-8")

            self.assertEqual(module.find_project_doc("Market Compare", project_dir), market_doc)
            self.assertIsNone(module.find_project_doc("Scheduler", project_dir))
            self.assertIsNone(module.find_project_doc("Missing Project", project_dir))

    def test_dirty_target_detection_raises_for_existing_target_changes(self):
        module = load_module()
        git = FakeGit(dirty_output=" M Note/Work/TianYan/AgentTracking/2026-05-22 Agent Tracking.md\n")

        with self.assertRaisesRegex(RuntimeError, "target files already have local changes"):
            module.ensure_targets_clean(
                Path("/vault"),
                [Path("/vault/Note/Work/TianYan/AgentTracking/2026-05-22 Agent Tracking.md")],
                git=git,
            )

    def test_record_workflow_uses_required_git_command_order(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            tracking_dir = vault / "Note/Work/TianYan/AgentTracking"
            project_dir = vault / "Note/Work/TianYan/项目文档"
            project_dir.mkdir(parents=True)
            (project_dir / "AgentTracking.md").write_text("# AgentTracking\n", encoding="utf-8")
            git = FakeGit()
            record = {
                "title": "实现 Agent 工作追踪 skill",
                "status": "completed",
                "repo": "/home/yanxin/personal/skills",
                "project": "AgentTracking",
                "summary": "创建记录脚本和 skill 指令。",
                "outputs": ["agent-work-tracker/SKILL.md"],
                "verification": ["python -m unittest"],
                "next_steps": ["重启 Codex 加载 skill"],
            }

            result = module.record_workflow(
                record,
                vault_root=vault,
                tracking_dir=tracking_dir,
                project_doc_dir=project_dir,
                today=date(2026, 5, 22),
                recorded_at="2026-05-22 18:30",
                git=git,
            )

            self.assertEqual(result["status"], "committed")
            self.assertEqual(
                git.commands,
                [
                    ["pull", "--rebase", "--autostash"],
                    [
                        "status",
                        "--porcelain",
                        "--",
                        "Note/Work/TianYan/AgentTracking/2026-05-22 Agent Tracking.md",
                        "Note/Work/TianYan/项目文档/AgentTracking.md",
                    ],
                    [
                        "add",
                        "--",
                        "Note/Work/TianYan/AgentTracking/2026-05-22 Agent Tracking.md",
                        "Note/Work/TianYan/项目文档/AgentTracking.md",
                    ],
                    ["diff", "--cached", "--quiet"],
                    ["commit", "-m", "docs: 记录 agent 工作进展"],
                    ["pull", "--rebase", "--autostash"],
                    ["push"],
                ],
            )
            self.assertTrue((tracking_dir / "2026-05-22 Agent Tracking.md").exists())
            self.assertIn(
                "[[2026-05-22 Agent Tracking]]",
                (project_dir / "AgentTracking.md").read_text(encoding="utf-8"),
            )

    def test_cli_reads_json_from_stdin_without_git_when_requested(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            payload = json.dumps(
                {
                    "title": "记录一次无 git 测试",
                    "summary": "验证 CLI 能写入追踪文件。",
                },
                ensure_ascii=False,
            )
            stdin = Mock()
            stdin.read.return_value = payload

            exit_code = module.main(
                [
                    "--config",
                    str(Path(tmp) / "missing-config.toml"),
                    "--vault-root",
                    str(vault),
                    "--today",
                    "2026-05-22",
                    "--recorded-at",
                    "2026-05-22 18:30",
                    "--no-git",
                ],
                stdin=stdin,
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(
                (
                    vault
                    / "Note/Work/TianYan/AgentTracking/2026-05-22 Agent Tracking.md"
                ).exists()
            )

    def test_cli_uses_config_file_for_destinations_and_git_policy(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vault = root / "vault"
            config_path = root / "config.toml"
            config_path.write_text(
                '\n'.join(
                    [
                        "[obsidian]",
                        'vault_root = "%s"' % vault,
                        'agent_tracking_dir = "Work/AgentTracking"',
                        'project_doc_dir = "Work/Projects"',
                        "",
                        "[git]",
                        "sync = false",
                    ]
                ),
                encoding="utf-8",
            )
            payload = json.dumps(
                {
                    "title": "配置文件测试",
                    "summary": "验证配置文件决定写入位置。",
                },
                ensure_ascii=False,
            )
            stdin = Mock()
            stdin.read.return_value = payload

            exit_code = module.main(
                [
                    "--config",
                    str(config_path),
                    "--today",
                    "2026-05-22",
                    "--recorded-at",
                    "2026-05-22 18:30",
                ],
                stdin=stdin,
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue((vault / "Work/AgentTracking/2026-05-22 Agent Tracking.md").exists())

    def test_cli_arguments_override_config_file_destinations(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_vault = root / "config-vault"
            cli_vault = root / "cli-vault"
            config_path = root / "config.toml"
            config_path.write_text(
                '\n'.join(
                    [
                        "[obsidian]",
                        'vault_root = "%s"' % config_vault,
                        'agent_tracking_dir = "Configured/Tracking"',
                        "",
                        "[git]",
                        "sync = false",
                    ]
                ),
                encoding="utf-8",
            )
            payload = json.dumps(
                {
                    "title": "CLI 覆盖测试",
                    "summary": "验证 CLI 参数优先于配置文件。",
                },
                ensure_ascii=False,
            )
            stdin = Mock()
            stdin.read.return_value = payload

            exit_code = module.main(
                [
                    "--config",
                    str(config_path),
                    "--vault-root",
                    str(cli_vault),
                    "--tracking-dir",
                    str(cli_vault / "Cli/Tracking"),
                    "--today",
                    "2026-05-22",
                    "--recorded-at",
                    "2026-05-22 18:30",
                ],
                stdin=stdin,
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue((cli_vault / "Cli/Tracking/2026-05-22 Agent Tracking.md").exists())
            self.assertFalse((config_vault / "Configured/Tracking/2026-05-22 Agent Tracking.md").exists())

    def test_default_config_path_uses_xdg_config_home(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            xdg_home = root / "xdg"
            vault = root / "vault"
            config_dir = xdg_home / "yx-workflow"
            config_dir.mkdir(parents=True)
            (config_dir / "config.toml").write_text(
                '\n'.join(
                    [
                        "[obsidian]",
                        'vault_root = "%s"' % vault,
                        'agent_tracking_dir = "Tracking"',
                        "",
                        "[git]",
                        "sync = false",
                    ]
                ),
                encoding="utf-8",
            )
            payload = json.dumps(
                {
                    "title": "默认配置路径测试",
                    "summary": "验证 XDG_CONFIG_HOME 下的配置会被读取。",
                },
                ensure_ascii=False,
            )
            stdin = Mock()
            stdin.read.return_value = payload
            old_xdg = os.environ.get("XDG_CONFIG_HOME")
            os.environ["XDG_CONFIG_HOME"] = str(xdg_home)
            try:
                exit_code = module.main(
                    [
                        "--today",
                        "2026-05-22",
                        "--recorded-at",
                        "2026-05-22 18:30",
                    ],
                    stdin=stdin,
                )
            finally:
                if old_xdg is None:
                    os.environ.pop("XDG_CONFIG_HOME", None)
                else:
                    os.environ["XDG_CONFIG_HOME"] = old_xdg

            self.assertEqual(exit_code, 0)
            self.assertTrue((vault / "Tracking/2026-05-22 Agent Tracking.md").exists())


if __name__ == "__main__":
    unittest.main()
