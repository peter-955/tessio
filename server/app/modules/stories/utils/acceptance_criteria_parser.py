import unicodedata

from pydantic import JsonValue

from app.modules.stories.domains.parsed_acceptance_criteria.entity import ParsedAcceptanceCriteria
from app.modules.stories.typing.constants import (
    ACCEPTANCE_CRITERIA_MARKERS,
    ATTRIBUTE_TEXT_NODE_TYPES,
    CONTAINER_NODE_TYPES,
    DEFAULT_HEADING_LEVEL,
    HARD_BREAK_NODE_TYPE,
    HEADING_NODE_TYPE,
    INLINE_CARD_NODE_TYPE,
    INLINE_NODE_TYPES,
    LINE_BREAK,
    LIST_NODE_TYPES,
    MARKER_PARAGRAPH_MAX_LENGTH,
    MARKER_PARAGRAPH_TRAILING_CHARACTERS,
    NESTED_ITEM_PREFIX,
    PARAGRAPH_NODE_TYPE,
    PLAIN_APOSTROPHE,
    TEXT_NODE_TYPE,
    TYPOGRAPHIC_APOSTROPHE,
)
from app.modules.stories.typing.enums import CriteriaSource
from app.modules.stories.utils.adf_nodes import (
    AdfNode,
    list_child_nodes,
    read_attribute_integer,
    read_attribute_text,
    read_node_type,
)


def parse_acceptance_criteria(description: JsonValue) -> ParsedAcceptanceCriteria:
    if not isinstance(description, dict):
        return ParsedAcceptanceCriteria(texts=[], source=CriteriaSource.NONE)
    blocks = _flatten_blocks(description)
    marker_position = _find_marker(blocks)
    if marker_position is None:
        first_list = next((block for block in blocks if read_node_type(block) in LIST_NODE_TYPES), None)
        if first_list is None:
            return ParsedAcceptanceCriteria(texts=[], source=CriteriaSource.NONE)
        return ParsedAcceptanceCriteria(texts=_extract_item_texts(first_list), source=CriteriaSource.FIRST_LIST)
    marker_index, marker_heading_level = marker_position
    marked_list = _find_list_after_marker(blocks[marker_index + 1 :], marker_heading_level)
    texts = [] if marked_list is None else _extract_item_texts(marked_list)
    return ParsedAcceptanceCriteria(texts=texts, source=CriteriaSource.MARKED_LIST)


def _flatten_blocks(node: AdfNode) -> list[AdfNode]:
    blocks: list[AdfNode] = []
    for child in list_child_nodes(node):
        if read_node_type(child) in CONTAINER_NODE_TYPES:
            blocks.extend(_flatten_blocks(child))
        else:
            blocks.append(child)
    return blocks


def _find_marker(blocks: list[AdfNode]) -> tuple[int, int | None] | None:
    for index, block in enumerate(blocks):
        node_type = read_node_type(block)
        if node_type == HEADING_NODE_TYPE and _contains_marker(_read_inline_text(block)):
            return index, _read_heading_level(block)
        if node_type == PARAGRAPH_NODE_TYPE and _is_marker_paragraph(_read_inline_text(block)):
            return index, None
    return None


def _is_marker_paragraph(text: str) -> bool:
    label = text.strip().rstrip(MARKER_PARAGRAPH_TRAILING_CHARACTERS).strip()
    return len(label) <= MARKER_PARAGRAPH_MAX_LENGTH and _contains_marker(label)


def _contains_marker(text: str) -> bool:
    normalized_text = _normalize_for_matching(text)
    return any(_normalize_for_matching(marker) in normalized_text for marker in ACCEPTANCE_CRITERIA_MARKERS)


def _normalize_for_matching(text: str) -> str:
    return unicodedata.normalize("NFC", text).replace(TYPOGRAPHIC_APOSTROPHE, PLAIN_APOSTROPHE).casefold()


def _read_heading_level(block: AdfNode) -> int:
    level = read_attribute_integer(block, "level")
    return DEFAULT_HEADING_LEVEL if level is None else level


def _find_list_after_marker(blocks: list[AdfNode], marker_heading_level: int | None) -> AdfNode | None:
    for block in blocks:
        node_type = read_node_type(block)
        if node_type in LIST_NODE_TYPES:
            return block
        if node_type == HEADING_NODE_TYPE and (
            marker_heading_level is None or _read_heading_level(block) <= marker_heading_level
        ):
            return None
    return None


def _extract_item_texts(list_node: AdfNode) -> list[str]:
    return [LINE_BREAK.join(lines) for lines in _read_list_items(list_node) if lines]


def _read_list_items(list_node: AdfNode) -> list[list[str]]:
    items: list[list[str]] = []
    for child in list_child_nodes(list_node):
        if read_node_type(child) in LIST_NODE_TYPES:
            nested_lines = _read_nested_lines(child)
            if items:
                items[-1].extend(nested_lines)
            else:
                items.append(nested_lines)
        else:
            items.append(_read_item_lines(child))
    return items


def _read_nested_lines(list_node: AdfNode) -> list[str]:
    return [NESTED_ITEM_PREFIX + line for item in _read_list_items(list_node) for line in item]


def _read_item_lines(item: AdfNode) -> list[str]:
    lines: list[str] = []
    inline_parts: list[str] = []
    for child in list_child_nodes(item):
        node_type = read_node_type(child)
        if node_type in INLINE_NODE_TYPES:
            inline_parts.append(_read_inline_text(child))
            continue
        lines.extend(_split_lines("".join(inline_parts)))
        inline_parts.clear()
        if node_type in LIST_NODE_TYPES:
            lines.extend(_read_nested_lines(child))
        else:
            lines.extend(_split_lines(_read_inline_text(child)))
    lines.extend(_split_lines("".join(inline_parts)))
    return lines


def _split_lines(text: str) -> list[str]:
    collapsed_lines = (" ".join(line.split()) for line in text.split(LINE_BREAK))
    return [line for line in collapsed_lines if line]


def _read_inline_text(node: AdfNode) -> str:
    node_type = read_node_type(node)
    if node_type == TEXT_NODE_TYPE:
        text = node.get("text")
        return text if isinstance(text, str) else ""
    if node_type == HARD_BREAK_NODE_TYPE:
        return LINE_BREAK
    if node_type in ATTRIBUTE_TEXT_NODE_TYPES:
        return read_attribute_text(node, "text")
    if node_type == INLINE_CARD_NODE_TYPE:
        return read_attribute_text(node, "url")
    return "".join(_read_inline_text(child) for child in list_child_nodes(node))
