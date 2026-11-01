from pydantic import JsonValue

type AdfNode = dict[str, JsonValue]


def read_node_type(node: AdfNode) -> str | None:
    node_type = node.get("type")
    return node_type if isinstance(node_type, str) else None


def list_child_nodes(node: AdfNode) -> list[AdfNode]:
    content = node.get("content")
    if not isinstance(content, list):
        return []
    return [child for child in content if isinstance(child, dict)]


def read_attribute_text(node: AdfNode, attribute_name: str) -> str:
    attributes = node.get("attrs")
    if not isinstance(attributes, dict):
        return ""
    value = attributes.get(attribute_name)
    return value if isinstance(value, str) else ""


def read_attribute_integer(node: AdfNode, attribute_name: str) -> int | None:
    attributes = node.get("attrs")
    if not isinstance(attributes, dict):
        return None
    value = attributes.get(attribute_name)
    return value if isinstance(value, int) and not isinstance(value, bool) else None
