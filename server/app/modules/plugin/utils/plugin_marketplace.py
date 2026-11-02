from app.modules.plugin.domains.plugin_bundle.entity import PluginBundle
from app.modules.plugin.typing.constants import (
    PLUGIN_MARKETPLACE_DESCRIPTION,
    PLUGIN_MARKETPLACE_NAME,
    PLUGIN_MARKETPLACE_OWNER,
    PLUGIN_ROUTE_PREFIX,
)


def build_plugin_marketplace(bundle: PluginBundle, public_url: str) -> dict[str, object]:
    archive_url = f"{public_url.rstrip('/')}{PLUGIN_ROUTE_PREFIX}/{bundle.file_name}"
    return {
        "name": PLUGIN_MARKETPLACE_NAME,
        "description": PLUGIN_MARKETPLACE_DESCRIPTION,
        "owner": {"name": PLUGIN_MARKETPLACE_OWNER},
        "plugins": [
            {
                "name": bundle.name,
                "description": bundle.description,
                "version": bundle.version,
                "source": {"source": "archive", "url": archive_url, "sha256": bundle.sha256},
            }
        ],
    }
