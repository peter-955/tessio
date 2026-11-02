import io
import json
import stat
import zipfile
from pathlib import Path

import pytest

from app.modules.plugin.errors import PluginManifestInvalidError
from app.modules.plugin.infrastructure import DirectoryPluginBundleLoader
from app.modules.plugin.utils.plugin_version import is_plugin_version_current


def write_plugin(root: Path, version: str = "1.2.3") -> Path:
    (root / ".claude-plugin").mkdir(parents=True)
    manifest = {"name": "tessio", "version": version, "description": "Test plugin"}
    (root / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest))
    (root / "skills" / "run").mkdir(parents=True)
    (root / "skills" / "run" / "SKILL.md").write_text("---\nname: run\n---\n")
    script = root / "scripts" / "tool.sh"
    script.parent.mkdir()
    script.write_text("#!/bin/sh\n")
    script.chmod(0o755)
    (root / "hooks" / "tests").mkdir(parents=True)
    (root / "hooks" / "tests" / "test_hook.py").write_text("")
    (root / "hooks" / "__pycache__").mkdir()
    (root / "hooks" / "__pycache__" / "hook.cpython-314.pyc").write_bytes(b"")
    return root


def test_the_bundle_is_named_after_the_manifest_and_leaves_tests_out(tmp_path: Path) -> None:
    bundle = DirectoryPluginBundleLoader(write_plugin(tmp_path)).load()

    assert (bundle.name, bundle.version, bundle.file_name) == ("tessio", "1.2.3", "tessio-1.2.3.zip")
    with zipfile.ZipFile(io.BytesIO(bundle.archive)) as archive:
        assert sorted(archive.namelist()) == [".claude-plugin/plugin.json", "scripts/tool.sh", "skills/run/SKILL.md"]
        script_mode = archive.getinfo("scripts/tool.sh").external_attr >> 16
    assert script_mode & stat.S_IXUSR


def test_the_archive_is_the_same_on_every_load(tmp_path: Path) -> None:
    plugin_dir = write_plugin(tmp_path)

    first = DirectoryPluginBundleLoader(plugin_dir).load()
    second = DirectoryPluginBundleLoader(plugin_dir).load()

    assert first.sha256 == second.sha256


@pytest.mark.parametrize("version", ["1.2", "v1.2.3", ""])
def test_a_manifest_without_a_semantic_version_is_refused(tmp_path: Path, version: str) -> None:
    with pytest.raises(PluginManifestInvalidError):
        DirectoryPluginBundleLoader(write_plugin(tmp_path, version)).load()


def test_a_missing_manifest_is_refused(tmp_path: Path) -> None:
    with pytest.raises(PluginManifestInvalidError):
        DirectoryPluginBundleLoader(tmp_path).load()


def write_contents(plugin_dir: Path) -> None:
    (plugin_dir / "skills" / "run" / "SKILL.md").write_text(
        "---\nname: run\ndescription: Run the tests\nargument-hint: <STORY-KEY>\n---\nBody\n"
    )
    (plugin_dir / "skills" / "bare").mkdir()
    (plugin_dir / "skills" / "bare" / "SKILL.md").write_text("No frontmatter\n")
    (plugin_dir / "commands").mkdir()
    (plugin_dir / "commands" / "status.md").write_text("---\ndescription: Show the status\n---\n")
    hooks = {
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": "mcp__plugin_tessio_tessio__finish_run",
                    "hooks": [
                        {"type": "command", "command": "python3 upload.py", "timeout": 60},
                        {"type": "prompt", "prompt": "Check the run"},
                    ],
                }
            ],
            "Stop": [{"hooks": [{"type": "command", "command": "./stop.sh"}]}],
        }
    }
    (plugin_dir / "hooks" / "hooks.json").write_text(json.dumps(hooks))
    mcp = {"mcpServers": {"tessio": {"type": "http", "url": "${user_config.tessio_url}/mcp", "headers": {"A": "1"}}}}
    (plugin_dir / ".mcp.json").write_text(json.dumps(mcp))


def test_the_bundle_lists_skills_commands_hooks_and_mcp_servers(tmp_path: Path) -> None:
    plugin_dir = write_plugin(tmp_path)
    write_contents(plugin_dir)

    bundle = DirectoryPluginBundleLoader(plugin_dir).load()

    assert [(skill.name, skill.description, skill.argument_hint) for skill in bundle.skills] == [
        ("bare", "", None),
        ("run", "Run the tests", "<STORY-KEY>"),
    ]
    assert [(command.name, command.description) for command in bundle.commands] == [("status", "Show the status")]
    assert [(hook.event, hook.matcher, hook.command, hook.timeout_seconds) for hook in bundle.hooks] == [
        ("PostToolUse", "mcp__plugin_tessio_tessio__finish_run", "python3 upload.py", 60),
        ("Stop", None, "./stop.sh", None),
    ]
    assert [(server.name, server.transport, server.url, server.header_names) for server in bundle.mcp_servers] == [
        ("tessio", "http", "${user_config.tessio_url}/mcp", ["A"])
    ]


def test_a_plugin_without_hooks_or_mcp_servers_has_empty_lists(tmp_path: Path) -> None:
    bundle = DirectoryPluginBundleLoader(write_plugin(tmp_path)).load()

    assert (bundle.commands, bundle.hooks, bundle.mcp_servers) == ([], [], [])


@pytest.mark.parametrize("skill_text", ["---\nname: [run\n---\n", "---\nname: run\n", "---\n- run\n---\n"])
def test_a_skill_with_broken_frontmatter_is_refused(tmp_path: Path, skill_text: str) -> None:
    plugin_dir = write_plugin(tmp_path)
    (plugin_dir / "skills" / "run" / "SKILL.md").write_text(skill_text)

    with pytest.raises(PluginManifestInvalidError):
        DirectoryPluginBundleLoader(plugin_dir).load()


@pytest.mark.parametrize(
    ("file_name", "text"), [("hooks/hooks.json", "{"), ("hooks/hooks.json", "[]"), (".mcp.json", "{}")]
)
def test_broken_hooks_or_mcp_files_are_refused(tmp_path: Path, file_name: str, text: str) -> None:
    plugin_dir = write_plugin(tmp_path)
    (plugin_dir / file_name).write_text(text)

    with pytest.raises(PluginManifestInvalidError):
        DirectoryPluginBundleLoader(plugin_dir).load()


@pytest.mark.parametrize(
    ("sent", "required", "is_current"),
    [
        ("0.2.0", "0.2.0", True),
        ("0.10.0", "0.9.0", True),
        ("1.0.0", "0.9.9", True),
        ("0.1.9", "0.2.0", False),
        (None, "0.2.0", False),
        ("0.2", "0.2.0", False),
    ],
)
def test_plugin_versions_compare_by_number(sent: str | None, required: str, is_current: bool) -> None:
    assert is_plugin_version_current(sent, required) is is_current
