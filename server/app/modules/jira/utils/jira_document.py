from pydantic import JsonValue

from app.modules.jira.domains.jira_document_block.entity import JiraDocumentBlock
from app.modules.jira.typing.constants import JIRA_ADF_HEADING_LEVEL, JIRA_ADF_VERSION
from app.modules.jira.typing.enums import JiraDocumentBlockKind


def build_adf_document(blocks: list[JiraDocumentBlock]) -> dict[str, JsonValue]:
    content: list[JsonValue] = [node for block in blocks for node in _build_nodes(block)]
    return {"type": "doc", "version": JIRA_ADF_VERSION, "content": content}


def render_jira_document_text(blocks: list[JiraDocumentBlock]) -> str:
    lines: list[str] = []
    for block in blocks:
        texts = _clean_texts(block)
        if not texts:
            continue
        if lines:
            lines.append("")
        if block.kind is JiraDocumentBlockKind.ORDERED_LIST:
            lines.extend(f"{position}. {text}" for position, text in enumerate(texts, start=1))
        elif block.kind is JiraDocumentBlockKind.BULLET_LIST:
            lines.extend(f"- {text}" for text in texts)
        elif block.kind is JiraDocumentBlockKind.LINK and block.link_url is not None:
            lines.append(f"{texts[0]}: {block.link_url}")
        else:
            lines.extend(texts)
    return "\n".join(lines)


def _build_nodes(block: JiraDocumentBlock) -> list[JsonValue]:
    texts = _clean_texts(block)
    if not texts:
        return []
    if block.kind is JiraDocumentBlockKind.HEADING:
        return [{"type": "heading", "attrs": {"level": JIRA_ADF_HEADING_LEVEL}, "content": [_text_node(texts[0])]}]
    if block.kind is JiraDocumentBlockKind.CODE:
        return [{"type": "codeBlock", "content": [_text_node("\n".join(texts))]}]
    if block.kind is JiraDocumentBlockKind.LINK and block.link_url is not None:
        link_mark: JsonValue = {"type": "link", "attrs": {"href": block.link_url}}
        return [{"type": "paragraph", "content": [{"type": "text", "text": texts[0], "marks": [link_mark]}]}]
    if block.kind in {JiraDocumentBlockKind.ORDERED_LIST, JiraDocumentBlockKind.BULLET_LIST}:
        list_type = "orderedList" if block.kind is JiraDocumentBlockKind.ORDERED_LIST else "bulletList"
        items: list[JsonValue] = [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [_text_node(text)]}]} for text in texts
        ]
        return [{"type": list_type, "content": items}]
    return [{"type": "paragraph", "content": [_text_node(text)]} for text in texts]


def _text_node(text: str) -> JsonValue:
    return {"type": "text", "text": text}


def _clean_texts(block: JiraDocumentBlock) -> list[str]:
    return [text.strip() for text in block.texts if text.strip()]
