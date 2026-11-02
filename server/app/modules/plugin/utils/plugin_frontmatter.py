import yaml

from app.modules.plugin.errors import PluginManifestInvalidError
from app.modules.plugin.typing.constants import PLUGIN_FRONTMATTER_DELIMITER


def read_frontmatter(text: str, source: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != PLUGIN_FRONTMATTER_DELIMITER:
        return {}
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == PLUGIN_FRONTMATTER_DELIMITER)
    except StopIteration as error:
        raise PluginManifestInvalidError(f"{source} has no closing frontmatter line") from error
    try:
        values = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as error:
        raise PluginManifestInvalidError(f"{source} has invalid frontmatter") from error
    if values is None:
        return {}
    if not isinstance(values, dict):
        raise PluginManifestInvalidError(f"{source} frontmatter is not a mapping")
    return {str(key): str(value) for key, value in values.items() if value is not None}
