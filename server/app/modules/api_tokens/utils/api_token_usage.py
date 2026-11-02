from datetime import datetime

from app.modules.api_tokens.domains.api_token.entity import ApiToken
from app.modules.api_tokens.typing.constants import LAST_USED_REFRESH_INTERVAL, MAXIMUM_PLUGIN_VERSION_LENGTH


def read_storable_plugin_version(plugin_version: str | None) -> str | None:
    if plugin_version is None:
        return None
    version = plugin_version.strip()
    return version if 0 < len(version) <= MAXIMUM_PLUGIN_VERSION_LENGTH else None


def build_usage_update(api_token: ApiToken, now: datetime, plugin_version: str | None) -> dict[str, object]:
    update: dict[str, object] = {}
    if plugin_version is not None and plugin_version != api_token.plugin_version:
        update["plugin_version"] = plugin_version
    if update or api_token.last_used_at is None or now - api_token.last_used_at >= LAST_USED_REFRESH_INTERVAL:
        update["last_used_at"] = now
    return update
