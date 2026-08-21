from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SkillLayoutTests(unittest.TestCase):
    def test_root_skill_is_yx_workflow_router(self):
        skill = ROOT / "SKILL.md"
        content = skill.read_text(encoding="utf-8")

        self.assertIn("name: yx-workflow", content)
        self.assertIn("skills/agent-work-tracker/", content)
        self.assertIn("skills/development-guidelines/", content)
        self.assertIn("skills/write-like-xin/", content)

    def test_agent_work_tracker_is_sub_skill(self):
        self.assertTrue((ROOT / "skills/agent-work-tracker/SKILL.md").is_file())
        self.assertTrue((ROOT / "skills/agent-work-tracker/scripts/record_work.py").is_file())
        self.assertTrue((ROOT / "skills/agent-work-tracker/config.example.toml").is_file())
        self.assertFalse((ROOT / "agent-work-tracker/SKILL.md").exists())

    def test_conventional_commit_zh_is_sub_skill(self):
        skill = ROOT / "skills/conventional-commit-zh"

        self.assertTrue((skill / "SKILL.md").is_file())
        self.assertTrue((skill / "agents/openai.yaml").is_file())
        self.assertFalse((ROOT / "conventional-commit-zh/SKILL.md").exists())

    def test_dev_machine_bootstrap_is_sub_skill(self):
        skill = ROOT / "skills/dev-machine-bootstrap"

        self.assertTrue((skill / "SKILL.md").is_file())
        self.assertTrue((skill / "scripts/inspect_host.sh").is_file())
        self.assertTrue((skill / "scripts/plan_bootstrap.sh").is_file())
        self.assertTrue((skill / "scripts/apply_bootstrap.sh").is_file())
        self.assertTrue((skill / "assets/tmux.conf").is_file())
        self.assertFalse((ROOT / "dev-machine-bootstrap/SKILL.md").exists())

    def test_orchestrated_worktree_implementation_is_sub_skill(self):
        skill = ROOT / "skills/orchestrated-worktree-implementation"

        self.assertTrue((skill / "SKILL.md").is_file())
        self.assertTrue((skill / "agents/openai.yaml").is_file())
        self.assertFalse((ROOT / "orchestrated-worktree-implementation/SKILL.md").exists())

    def test_development_guidelines_is_sub_skill(self):
        skill = ROOT / "skills/development-guidelines"

        self.assertTrue((skill / "SKILL.md").is_file())
        self.assertTrue((skill / "agents/openai.yaml").is_file())
        self.assertTrue((skill / "references/boolean-naming.md").is_file())
        self.assertFalse((ROOT / "development-guidelines/SKILL.md").exists())

    def test_write_chinese_is_sub_skill(self):
        skill = ROOT / "skills/write-chinese"

        self.assertTrue((skill / "SKILL.md").is_file())
        self.assertTrue((skill / "agents/openai.yaml").is_file())
        self.assertFalse((ROOT / "write-chinese/SKILL.md").exists())

    def test_write_like_xin_is_sub_skill(self):
        skill = ROOT / "skills/write-like-xin"

        self.assertTrue((skill / "SKILL.md").is_file())
        self.assertTrue((skill / "agents/openai.yaml").is_file())
        self.assertFalse((ROOT / "write-like-xin/SKILL.md").exists())

    def test_multi_repo_manager_is_sub_skill(self):
        skill = ROOT / "skills/multi-repo-manager"

        self.assertTrue((skill / "SKILL.md").is_file())
        self.assertTrue((skill / "agents/openai.yaml").is_file())
        content = (skill / "SKILL.md").read_text(encoding="utf-8")
        metadata = (skill / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn("### Audit", content)
        self.assertIn("explicit cleanup authorization", content)
        self.assertIn('display_name: "Multi-Repo Manager"', metadata)
        self.assertIn("$multi-repo-manager", metadata)
        self.assertIn(
            "skills/multi-repo-manager/",
            (ROOT / "SKILL.md").read_text(encoding="utf-8"),
        )
        self.assertIn("### multi-repo-manager", (ROOT / "README.md").read_text())
        self.assertFalse((ROOT / "multi-repo-manager/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
