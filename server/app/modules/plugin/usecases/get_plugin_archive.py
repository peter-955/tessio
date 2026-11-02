from app.modules.plugin.domains.plugin_bundle.entity import PluginBundle
from app.modules.plugin.errors import PluginArchiveNotFoundError


class GetPluginArchiveUseCase:
    def __init__(self, bundle: PluginBundle) -> None:
        self._bundle = bundle

    def execute(self, file_name: str) -> PluginBundle:
        if file_name != self._bundle.file_name:
            raise PluginArchiveNotFoundError
        return self._bundle
