from __future__ import annotations

import json
import re
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
EXPECTED_SKILLS = {
    "run-story-tests",
    "rerun-failed",
    "review-readiness",
    "import-cases",
    "draft-cases",
    "answer-gaps",
    "run-suite",
}
RUN_SKILL_TOOLS = {"mcp__plugin_tessio_tessio__*", "mcp__claude-in-chrome__*", "Bash(curl:*)", "Bash(mkdir:*)"}
SHARED_RUN_PROCEDURE_LINK = "../run-story-tests/references/execute-cases.md"
SKILL_LISTING_DOCUMENTS = (PLUGIN_ROOT / "README.md", REPOSITORY_ROOT / "docs" / "guides" / "claude-setup.md")
MARKDOWN_LINK_PATTERN = re.compile(r"\]\(([^)\s]+)\)")
PLUGIN_ROOT_REFERENCE_PATTERN = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)")
EXTERNAL_LINK_PREFIXES = ("http://", "https://", "mailto:", "#")
YAML_INDICATOR_CHARACTERS = tuple("[]{}*&!|>@`%,?#")
GAP_PROCEDURE_LINK = "../answer-gaps/references/when-gaps-block.md"


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


def read_frontmatter(skill_file: Path) -> dict[str, str]:
    lines = skill_file.read_text().split("---", 2)[1].strip().splitlines()
    return {line.split(":", 1)[0]: line.split(":", 1)[1].strip() for line in lines}


def list_skill_documents() -> list[Path]:
    return sorted((PLUGIN_ROOT / "skills").rglob("*.md"))


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

    def test_mcp_server_sends_the_manifest_version(self) -> None:
        manifest = load_json(PLUGIN_ROOT / ".claude-plugin" / "plugin.json")
        server = as_object(as_object(load_json(PLUGIN_ROOT / ".mcp.json")["mcpServers"])["tessio"])
        self.assertEqual(as_object(server["headers"])["X-Tessio-Plugin-Version"], manifest["version"])
        self.assertRegex(str(manifest["version"]), r"^\d+\.\d+\.\d+$")

    def test_hook_matches_the_plugin_tool_name(self) -> None:
        hooks_configuration = load_json(PLUGIN_ROOT / "hooks" / "hooks.json")
        post_tool_use = as_list(as_object(hooks_configuration["hooks"])["PostToolUse"])
        scripts_by_matcher = {
            str(as_object(entry)["matcher"]): str(as_object(as_list(as_object(entry)["hooks"])[0])["command"])
            for entry in post_tool_use
        }
        self.assertEqual(
            set(scripts_by_matcher),
            {"mcp__plugin_tessio_tessio__record_case_result", "mcp__plugin_tessio_tessio__finish_run"},
        )
        self.assertIn(
            "${CLAUDE_PLUGIN_ROOT}/hooks/upload_screenshots.py",
            scripts_by_matcher["mcp__plugin_tessio_tessio__record_case_result"],
        )
        self.assertIn(
            "${CLAUDE_PLUGIN_ROOT}/hooks/upload_run_log.py", scripts_by_matcher["mcp__plugin_tessio_tessio__finish_run"]
        )

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

    def test_skill_frontmatter_values_are_plain_yaml_strings(self) -> None:
        for skill_file in sorted((PLUGIN_ROOT / "skills").glob("*/SKILL.md")):
            for key, value in read_frontmatter(skill_file).items():
                is_quoted = len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'"
                if not is_quoted:
                    self.assertFalse(value.startswith(YAML_INDICATOR_CHARACTERS), f"{skill_file}: {key}")
                    self.assertNotIn(": ", value, f"{skill_file}: {key}")

    def test_skills_reference_only_bundled_files(self) -> None:
        for document in list_skill_documents():
            text = document.read_text()
            for target in MARKDOWN_LINK_PATTERN.findall(text):
                if target.startswith(EXTERNAL_LINK_PREFIXES):
                    continue
                linked_file = (document.parent / target.split("#", 1)[0]).resolve()
                self.assertTrue(linked_file.is_file(), f"{document}: {target}")
                self.assertTrue(linked_file.is_relative_to(PLUGIN_ROOT), f"{document}: {target}")
            for relative_path in PLUGIN_ROOT_REFERENCE_PATTERN.findall(text):
                self.assertTrue((PLUGIN_ROOT / relative_path).is_file(), f"{document}: {relative_path}")

    def test_answer_gaps_skill_uses_the_gap_tools_and_only_reads_code(self) -> None:
        skill_file = PLUGIN_ROOT / "skills" / "answer-gaps" / "SKILL.md"
        frontmatter = read_frontmatter(skill_file)
        allowed_tools = {tool.strip() for tool in frontmatter["allowed-tools"].split(",")}
        self.assertEqual(allowed_tools, {"mcp__plugin_tessio_tessio__*", "Read", "Grep", "Glob", "AskUserQuestion"})
        self.assertEqual(frontmatter["argument-hint"], '"[STORY-KEY | mine]"')
        skill = skill_file.read_text()
        for expected_text in (
            "get_my_gaps",
            "get_story_context",
            "answer_gap(gap_id, answer)",
            "reassign_gap",
            "set_test_data(key, value, kind, environment?)",
            "AskUserQuestion",
            "similar_answers",
            "path:line",
            "test_data_url",
            "Nothing is saved without the person's confirmation",
            "I found no source for this",
            "Never ask for a secret value",
            "Never edit test cases, Jira, files or code",
            "/tessio:run-story-tests",
            "references/when-gaps-block.md",
        ):
            self.assertIn(expected_text, skill)

    def test_run_skills_send_blocked_runs_to_the_gap_procedure(self) -> None:
        procedure = (PLUGIN_ROOT / "skills" / "answer-gaps" / "references" / "when-gaps-block.md").read_text()
        for expected_text in (
            "OPEN_GAPS_BLOCK_RUN",
            "GAPS_OPEN",
            "get_open_gaps",
            "get_my_gaps",
            "assignee_name",
            "assignee_role",
            "is_assignee_deactivated",
            "/tessio:answer-gaps",
        ):
            self.assertIn(expected_text, procedure)
        self.assertIn("a suite run (`/tessio:run-suite`)", procedure)
        self.assertIn("get_my_gaps()", procedure)
        for skill_name in ("run-story-tests", "rerun-failed", "run-suite"):
            skill = (PLUGIN_ROOT / "skills" / skill_name / "SKILL.md").read_text()
            self.assertIn(GAP_PROCEDURE_LINK, skill, skill_name)
            self.assertIn("OPEN_GAPS_BLOCK_RUN", skill, skill_name)

    def test_run_suite_skill_runs_batches_of_at_most_fifty_cases(self) -> None:
        skill_file = PLUGIN_ROOT / "skills" / "run-suite" / "SKILL.md"
        frontmatter = read_frontmatter(skill_file)
        allowed_tools = {tool.strip() for tool in frontmatter["allowed-tools"].split(",")}
        self.assertEqual(allowed_tools, RUN_SKILL_TOOLS)
        self.assertEqual(frontmatter["argument-hint"], "<suite> [environment] [case codes]")
        skill = skill_file.read_text()
        self.assertLess(skill.index("get_suite_context(suite)"), skill.index("start_run(suite=<suite id>"))
        for expected_text in (
            "at most **50 cases**",
            "batches** of at most 50 cases",
            "start_run(suite=<suite id>, environment)` without `case_ids`",
            "start_run(suite=<suite id>, environment, case_ids=<the batch's case ids>)",
            "Start the next batch only after `finish_run` of the previous one",
            "skipped_cases",
            "is_default",
            SHARED_RUN_PROCEDURE_LINK,
            GAP_PROCEDURE_LINK,
            "OPEN_GAPS_BLOCK_RUN",
            "SUITE_ALREADY_RUNNING",
            "SUITE_ARCHIVED",
            "SUITE_EMPTY",
            "CASE_NOT_READY",
            "NOT_FOUND",
            '/tessio:run-suite "<suite name>" <environment> <codes of the cases that did not run>',
            "/tessio:rerun-failed <run-id>",
            "never changes a story's test status",
        ):
            self.assertIn(expected_text, skill)
        self.assertNotIn("GAPS_OPEN`", skill)

    def test_run_skills_share_the_run_procedure(self) -> None:
        for skill_name in ("rerun-failed", "run-suite"):
            skill_file = PLUGIN_ROOT / "skills" / skill_name / "SKILL.md"
            allowed_tools = {tool.strip() for tool in read_frontmatter(skill_file)["allowed-tools"].split(",")}
            self.assertEqual(allowed_tools, RUN_SKILL_TOOLS, skill_name)
            self.assertIn(SHARED_RUN_PROCEDURE_LINK, skill_file.read_text(), skill_name)

    def test_rerun_failed_skill_reruns_story_and_suite_runs(self) -> None:
        skill = (PLUGIN_ROOT / "skills" / "rerun-failed" / "SKILL.md").read_text()
        for expected_text in (
            "get_failed_cases(run_id)",
            "start_run(story_key, environment, parent_run_id=run_id)",
            "start_run(suite=<suite>, environment, parent_run_id=run_id)",
            "SUITE_ALREADY_RUNNING",
        ):
            self.assertIn(expected_text, skill)

    def test_rerun_failed_skill_splits_more_than_fifty_failed_cases_into_runs(self) -> None:
        skill = (PLUGIN_ROOT / "skills" / "rerun-failed" / "SKILL.md").read_text()
        for expected_text in (
            "at most **50 cases**",
            "A suite run with **more than 50 cases**",
            "get_suite_context(<suite>)",
            "batches** of at most 50 cases",
            "start_run(suite=<suite id>, environment, case_ids=<the batch's case ids>)",
            "Start the next batch only after `finish_run` of the previous one",
            "either `parent_run_id` or `case_ids`, never both",
            "One child run, linked to the parent",
            '/tessio:run-suite "<suite name>" <environment> <codes of the cases that did not run>',
            "NO_FAILED_CASES_TO_RERUN",
        ):
            self.assertIn(expected_text, skill)
        self.assertLess(skill.index("get_failed_cases(run_id)"), skill.index("get_suite_context(<suite>)"))
        self.assertLess(
            skill.index("start_run(suite=<suite>, environment, parent_run_id=run_id)"),
            skill.index("start_run(suite=<suite id>, environment, case_ids="),
        )
        self.assertNotIn("case_ids=<the batch's case ids>, parent_run_id", skill)

    def test_run_suite_skill_asks_again_when_the_environment_was_archived(self) -> None:
        skill = (PLUGIN_ROOT / "skills" / "run-suite" / "SKILL.md").read_text()
        for expected_text in (
            "`UNKNOWN_REFERENCE` on a case",
            "`UNKNOWN_REFERENCE` naming an environment",
            "the environment was archived",
            "list its `environments` names, and ask the user",
        ):
            self.assertIn(expected_text, skill)

    def test_gap_procedure_finds_every_blocked_story_of_a_cut_off_suite_refusal(self) -> None:
        procedure = (PLUGIN_ROOT / "skills" / "answer-gaps" / "references" / "when-gaps-block.md").read_text()
        for expected_text in (
            'ends with "; and N more"',
            "get_suite_context(suite)",
            "`stories[].key`",
            "`skipped_cases[].story_key`",
            "Call `get_open_gaps(story_key)` for each candidate",
            "no severity, no target and no deactivated assignee",
            "never from the message",
        ):
            self.assertIn(expected_text, procedure)
        self.assertNotIn("When a refusal lists the blocked stories or gaps, use that list", procedure)

    def test_docs_list_every_skill(self) -> None:
        for document in SKILL_LISTING_DOCUMENTS:
            text = document.read_text()
            for skill_name in sorted(EXPECTED_SKILLS):
                self.assertIn(f"`/tessio:{skill_name}", text, f"{document}: {skill_name}")
        self.assertIn("| `get_suite_context` | `run.view` |", (PLUGIN_ROOT / "README.md").read_text())

    def test_shared_procedure_covers_the_run_rules(self) -> None:
        procedure = (PLUGIN_ROOT / "skills" / "run-story-tests" / "references" / "execute-cases.md").read_text()
        for expected_text in (
            "curl -fsS",
            "finish_run",
            "scale: 0.5",
            "save_to_disk: true",
            "resolve_data",
            "read_console_messages",
            "read_network_requests",
            "suspected_cause",
        ):
            self.assertIn(expected_text, procedure)

    def test_shared_procedure_records_one_result_per_iteration(self) -> None:
        procedure = (PLUGIN_ROOT / "skills" / "run-story-tests" / "references" / "execute-cases.md").read_text()
        for expected_text in (
            "Shared steps are already expanded",
            "`parameters` and `data_rows`",
            "run the whole case once per data row, in row order",
            "numbered from 0",
            "{{param.<name>}}",
            "one `record_case_result` per iteration",
            "iteration=<row index>",
            "CASE_RESULT_EXISTS",
            "ITERATION_OUT_OF_RANGE",
            "A failed or blocked iteration ends only that iteration",
            "A case without `data_rows` runs once, with no `iteration`",
        ):
            self.assertIn(expected_text, procedure)
        self.assertLess(procedure.index("iteration=<row index>"), procedure.index("finish_run(run_id, summary)"))
        readme = (PLUGIN_ROOT / "README.md").read_text()
        self.assertIn("one `record_case_result` per row with `iteration`", readme)

    def test_case_creation_procedure_checks_confirms_and_keeps_secrets_out(self) -> None:
        procedure = (PLUGIN_ROOT / "skills" / "import-cases" / "references" / "create-cases.md").read_text()
        for expected_text in ("check_draft_cases", "create_draft_cases", "as Draft?", "{{data.<key>}}", "Never invent"):
            self.assertIn(expected_text, procedure)

    def test_import_skill_runs_the_bundled_extractor(self) -> None:
        skill = (PLUGIN_ROOT / "skills" / "import-cases" / "SKILL.md").read_text()
        self.assertIn("Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/extract_file.py *)", skill)
        self.assertIn("python3 ${CLAUDE_PLUGIN_ROOT}/scripts/extract_file.py <file>", skill)
        self.assertTrue((PLUGIN_ROOT / "scripts" / "extract_file.py").is_file())


if __name__ == "__main__":
    unittest.main()
