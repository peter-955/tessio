from app.modules.plugin.domains.plugin_hook.entity import PluginHook
from app.modules.plugin.errors import PluginManifestInvalidError
from app.modules.plugin.typing.constants import PLUGIN_HOOK_COMMAND_TYPE


def read_timeout_seconds(handler: dict[str, object]) -> int | None:
    timeout = handler.get("timeout")
    return timeout if isinstance(timeout, int) else None


def build_plugin_hooks(document: object) -> list[PluginHook]:
    events = document.get("hooks") if isinstance(document, dict) else None
    if not isinstance(events, dict):
        raise PluginManifestInvalidError("hooks/hooks.json has no 'hooks' object")
    hooks: list[PluginHook] = []
    for event, groups in events.items():
        for group in groups if isinstance(groups, list) else []:
            if not isinstance(group, dict):
                continue
            matcher = group.get("matcher")
            for handler in group.get("hooks", []):
                if not isinstance(handler, dict) or handler.get("type") != PLUGIN_HOOK_COMMAND_TYPE:
                    continue
                hooks.append(
                    PluginHook(
                        event=str(event),
                        matcher=matcher if isinstance(matcher, str) and matcher else None,
                        command=str(handler.get("command", "")),
                        timeout_seconds=read_timeout_seconds(handler),
                    )
                )
    return hooks
