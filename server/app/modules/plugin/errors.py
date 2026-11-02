from app.modules.plugin.typing.constants import PLUGIN_UPDATE_COMMAND
from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class PluginOutdatedError(TessioError):
    def __init__(self, sent_version: str | None, required_version: str) -> None:
        self.sent_version = sent_version
        self.required_version = required_version
        installed = f"version {sent_version}" if sent_version else "no version"
        super().__init__(
            ErrorCode.PLUGIN_OUTDATED,
            f"Your Tessio plugin sent {installed}; this Tessio needs {required_version}. "
            f"Run `{PLUGIN_UPDATE_COMMAND}`, then restart Claude Code.",
        )


class PluginArchiveNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Plugin archive not found.")


class PluginManifestInvalidError(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(f"The Tessio plugin manifest is invalid: {reason}")
