from pydantic import JsonValue


def build_plain_text_document(text: str | None) -> JsonValue:
    if text is None or not text.strip():
        return None
    paragraphs: list[JsonValue] = [
        {"type": "paragraph", "content": [{"type": "text", "text": line}]} if line else {"type": "paragraph"}
        for line in text.strip().splitlines()
    ]
    return {"type": "doc", "version": 1, "content": paragraphs}


def read_plain_text(document: JsonValue) -> str:
    if not isinstance(document, dict):
        return ""
    paragraphs = document.get("content")
    if not isinstance(paragraphs, list):
        return ""
    lines = []
    for paragraph in paragraphs:
        texts = paragraph.get("content") if isinstance(paragraph, dict) else None
        lines.append(
            "".join(str(node.get("text", "")) for node in texts if isinstance(node, dict))
            if isinstance(texts, list)
            else ""
        )
    return "\n".join(lines)
