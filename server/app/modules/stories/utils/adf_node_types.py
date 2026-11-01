from pydantic import JsonValue

from app.modules.stories.utils.adf_nodes import AdfNode, list_child_nodes, read_node_type


def collect_node_types(description: JsonValue) -> frozenset[str]:
    if not isinstance(description, dict):
        return frozenset()
    node_types: set[str] = set()
    pending_nodes: list[AdfNode] = [description]
    while pending_nodes:
        node = pending_nodes.pop()
        node_type = read_node_type(node)
        if node_type is not None:
            node_types.add(node_type)
        pending_nodes.extend(list_child_nodes(node))
    return frozenset(node_types)
