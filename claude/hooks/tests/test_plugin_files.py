from __future__ import annotations

import json
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = PLUGIN_ROOT.parent
ALLOWED_USER_CONFIG_KEYS = {
    "type",
    "title",
    "description",
    "required",
    "default",
    "options",
    "multiple",
    "sensitive",
    "min",
    "max",
}
EXPECTED_SKILLS = {"run-story-tests", "rerun-failed", "review-readiness"}


def as_object(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise AssertionError(f"{value!r} is not a JSON object")
    return value


def as_list(value: object) -> list[object]:
    if not isinstance(value, list):
        raise AssertionError(f"{value!r} is not a JSON list")
    return value


def load_json(path: Path) -> dict[str, object]:
    return as_object(json.loads(path.read_text()))


class PluginFilesTest(unittest.TestCase):
    def test_plugin_manifest_declares_the_user_config(self) -> None:
        manifest = load_json(PLUGIN_ROOT / ".claude-plugin" / "plugin.json")
        self.assertEqual(manifest["name"], "tessio")
        user_config = as_object(manifest["userConfig"])
        self.assertEqual(set(user_config), {"tessio_url", "tessio_token"})
        for option_name in user_config:
            option = as_object(user_config[option_name])
            self.assertLessEqual(set(option), ALLOWED_USER_CONFIG_KEYS, option_name)
        self.assertIs(as_object(user_config["tessio_token"])["sensitive"], True)

    def test_mcp_server_uses_the_user_config(self) -> None:
        mcp_configuration = load_json(PLUGIN_ROOT / ".mcp.json")
        server = as_object(as_object(mcp_configuration["mcpServers"])["tessio"])
        self.assertEqual(server["type"], "http")
        self.assertEqual(server["url"], "${user_config.tessio_url}/mcp")
        self.assertEqual(as_object(server["headers"])["Authorization"], "Bearer ${user_config.tessio_token}")

    def test_hook_matches_the_plugin_tool_name(self) -> None:
        hooks_configuration = load_json(PLUGIN_ROOT / "hooks" / "hooks.json")
        post_tool_use = as_list(as_object(hooks_configuration["hooks"])["PostToolUse"])
        self.assertEqual(len(post_tool_use), 1)
        entry = as_object(post_tool_use[0])
        self.assertEqual(entry["matcher"], "mcp__plugin_tessio_tessio__record_case_result")
        command_hook = as_object(as_list(entry["hooks"])[0])
        self.assertEqual(command_hook["type"], "command")
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/hooks/upload_screenshots.py", str(command_hook["command"]))

    def test_marketplace_points_at_the_plugin_folder(self) -> None:
        marketplace = load_json(REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json")
        plugin = as_object(as_list(marketplace["plugins"])[0])
        self.assertEqual(plugin["name"], "tessio")
        self.assertEqual(plugin["source"], "./claude")

    def test_skills_have_frontmatter(self) -> None:
        skill_files = sorted((PLUGIN_ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual({skill_file.parent.name for skill_file in skill_files}, EXPECTED_SKILLS)
        for skill_file in skill_files:
            text = skill_file.read_text()
            self.assertTrue(text.startswith("---\n"), skill_file)
            frontmatter = text.split("---", 2)[1]
            self.assertIn(f"\nname: {skill_file.parent.name}\n", frontmatter, skill_file)
            self.assertIn("\ndescription: ", frontmatter, skill_file)
            self.assertIn("\nallowed-tools: ", frontmatter, skill_file)

    def test_shared_procedure_covers_the_run_rules(self) -> None:
        procedure = (PLUGIN_ROOT / "skills" / "run-story-tests" / "references" / "execute-cases.md").read_text()
        for expected_text in ("curl -fsS", "finish_run", "scale: 0.5", "save_to_disk: true", "resolve_data"):
            self.assertIn(expected_text, procedure)


if __name__ == "__main__":
    unittest.main()
