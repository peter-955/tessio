from app.modules.plugin.errors import PluginOutdatedError
from app.modules.plugin.utils.plugin_version import is_plugin_version_current


class CheckPluginVersionUseCase:
    def __init__(self, required_version: str) -> None:
        self._required_version = required_version

    def execute(self, sent_version: str | None) -> None:
        if not is_plugin_version_current(sent_version, self._required_version):
            raise PluginOutdatedError(sent_version, self._required_version)
