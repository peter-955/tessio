import hashlib
import io
import json
import stat
import zipfile
from pathlib import Path

from app.modules.plugin.domains.plugin_bundle.entity import PluginBundle
from app.modules.plugin.domains.plugin_command.entity import PluginCommand
from app.modules.plugin.domains.plugin_hook.entity import PluginHook
from app.modules.plugin.domains.plugin_mcp_server.entity import PluginMcpServer
from app.modules.plugin.domains.plugin_skill.entity import PluginSkill
from app.modules.plugin.errors import PluginManifestInvalidError
from app.modules.plugin.typing.constants import (
    PLUGIN_ARCHIVE_FILE_TEMPLATE,
    PLUGIN_ARCHIVE_TIMESTAMP,
    PLUGIN_COMMAND_SUFFIX,
    PLUGIN_COMMANDS_DIR,
    PLUGIN_EXCLUDED_PARTS,
    PLUGIN_EXCLUDED_SUFFIXES,
    PLUGIN_EXECUTABLE_MODE,
    PLUGIN_FILE_MODE,
    PLUGIN_HOOKS_PATH,
    PLUGIN_MANIFEST_PATH,
    PLUGIN_MCP_SERVERS_PATH,
    PLUGIN_SKILL_FILE_NAME,
    PLUGIN_SKILLS_DIR,
)
from app.modules.plugin.utils.plugin_frontmatter import read_frontmatter
from app.modules.plugin.utils.plugin_hooks import build_plugin_hooks
from app.modules.plugin.utils.plugin_mcp_servers import build_plugin_mcp_servers
from app.modules.plugin.utils.plugin_version import parse_plugin_version


def read_manifest_text(manifest: dict[str, object], key: str) -> str:
    value = manifest.get(key)
    if not isinstance(value, str) or not value:
        raise PluginManifestInvalidError(f"'{key}' is missing")
    return value


def list_plugin_files(plugin_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in plugin_dir.rglob("*")
        if path.is_file()
        and not PLUGIN_EXCLUDED_PARTS.intersection(path.relative_to(plugin_dir).parts)
        and path.suffix not in PLUGIN_EXCLUDED_SUFFIXES
    )


def build_archive(plugin_dir: Path) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in list_plugin_files(plugin_dir):
            info = zipfile.ZipInfo(path.relative_to(plugin_dir).as_posix(), PLUGIN_ARCHIVE_TIMESTAMP)
            is_executable = bool(path.stat().st_mode & stat.S_IXUSR)
            mode = PLUGIN_EXECUTABLE_MODE if is_executable else PLUGIN_FILE_MODE
            info.external_attr = (stat.S_IFREG | mode) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    return buffer.getvalue()


def read_json_file(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise PluginManifestInvalidError(f"{path.name} is not valid JSON") from error


def load_skills(plugin_dir: Path) -> list[PluginSkill]:
    skills: list[PluginSkill] = []
    for skill_file in sorted((plugin_dir / PLUGIN_SKILLS_DIR).glob(f"*/{PLUGIN_SKILL_FILE_NAME}")):
        frontmatter = read_frontmatter(skill_file.read_text(), skill_file.relative_to(plugin_dir).as_posix())
        skills.append(
            PluginSkill(
                name=frontmatter.get("name", skill_file.parent.name),
                description=frontmatter.get("description", ""),
                argument_hint=frontmatter.get("argument-hint"),
            )
        )
    return skills


def load_commands(plugin_dir: Path) -> list[PluginCommand]:
    commands: list[PluginCommand] = []
    for command_file in sorted((plugin_dir / PLUGIN_COMMANDS_DIR).glob(f"*{PLUGIN_COMMAND_SUFFIX}")):
        frontmatter = read_frontmatter(command_file.read_text(), command_file.relative_to(plugin_dir).as_posix())
        commands.append(
            PluginCommand(
                name=command_file.stem,
                description=frontmatter.get("description", ""),
                argument_hint=frontmatter.get("argument-hint"),
            )
        )
    return commands


def load_hooks(plugin_dir: Path) -> list[PluginHook]:
    hooks_path = plugin_dir / PLUGIN_HOOKS_PATH
    return build_plugin_hooks(read_json_file(hooks_path)) if hooks_path.is_file() else []


def load_mcp_servers(plugin_dir: Path) -> list[PluginMcpServer]:
    mcp_path = plugin_dir / PLUGIN_MCP_SERVERS_PATH
    return build_plugin_mcp_servers(read_json_file(mcp_path)) if mcp_path.is_file() else []


class DirectoryPluginBundleLoader:
    def __init__(self, plugin_dir: Path) -> None:
        self._plugin_dir = plugin_dir

    def load(self) -> PluginBundle:
        manifest_path = self._plugin_dir / PLUGIN_MANIFEST_PATH
        if not manifest_path.is_file():
            raise PluginManifestInvalidError(f"{manifest_path} not found")
        manifest = json.loads(manifest_path.read_text())
        if not isinstance(manifest, dict):
            raise PluginManifestInvalidError("it is not a JSON object")
        name = read_manifest_text(manifest, "name")
        version = read_manifest_text(manifest, "version")
        if parse_plugin_version(version) is None:
            raise PluginManifestInvalidError(f"version {version} is not MAJOR.MINOR.PATCH")
        archive = build_archive(self._plugin_dir)
        return PluginBundle(
            name=name,
            version=version,
            description=read_manifest_text(manifest, "description"),
            file_name=PLUGIN_ARCHIVE_FILE_TEMPLATE.format(name=name, version=version),
            sha256=hashlib.sha256(archive).hexdigest(),
            archive=archive,
            skills=load_skills(self._plugin_dir),
            commands=load_commands(self._plugin_dir),
            hooks=load_hooks(self._plugin_dir),
            mcp_servers=load_mcp_servers(self._plugin_dir),
        )
