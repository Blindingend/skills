from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SkillLayoutTests(unittest.TestCase):
    def test_root_skill_is_yx_workflow_router(self):
        skill = ROOT / "SKILL.md"
        content = skill.read_text(encoding="utf-8")

        self.assertIn("name: yx-workflow", content)
        self.assertIn("skills/agent-work-tracker/", content)

    def test_agent_work_tracker_is_sub_skill(self):
        self.assertTrue((ROOT / "skills/agent-work-tracker/SKILL.md").is_file())
        self.assertTrue((ROOT / "skills/agent-work-tracker/scripts/record_work.py").is_file())
        self.assertFalse((ROOT / "agent-work-tracker/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
