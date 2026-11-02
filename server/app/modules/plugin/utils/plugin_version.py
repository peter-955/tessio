import re

VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def parse_plugin_version(text: str | None) -> tuple[int, int, int] | None:
    match = VERSION_PATTERN.match((text or "").strip())
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def is_plugin_version_current(sent_version: str | None, required_version: str) -> bool:
    sent = parse_plugin_version(sent_version)
    required = parse_plugin_version(required_version)
    return sent is not None and required is not None and sent >= required
