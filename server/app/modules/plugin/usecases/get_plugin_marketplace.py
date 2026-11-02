from app.modules.plugin.domains.plugin_bundle.entity import PluginBundle
from app.modules.plugin.utils.plugin_marketplace import build_plugin_marketplace


class GetPluginMarketplaceUseCase:
    def __init__(self, bundle: PluginBundle, public_url: str) -> None:
        self._bundle = bundle
        self._public_url = public_url

    def execute(self) -> dict[str, object]:
        return build_plugin_marketplace(self._bundle, self._public_url)
