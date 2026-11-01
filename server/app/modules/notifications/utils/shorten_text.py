from app.modules.notifications.typing.constants import MAX_PAYLOAD_TEXT_LENGTH, TRUNCATION_MARK


def shorten_text(text: str) -> str:
    stripped_text = text.strip()
    if len(stripped_text) <= MAX_PAYLOAD_TEXT_LENGTH:
        return stripped_text
    return stripped_text[: MAX_PAYLOAD_TEXT_LENGTH - len(TRUNCATION_MARK)] + TRUNCATION_MARK
