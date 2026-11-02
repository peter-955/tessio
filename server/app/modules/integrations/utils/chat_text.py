from app.modules.integrations.typing.constants import CHAT_EXECUTOR_LABELS

ELLIPSIS = "…"


def shorten_chat_text(text: str, limit: int) -> str:
    stripped_text = text.strip()
    if len(stripped_text) <= limit:
        return stripped_text
    return stripped_text[: limit - len(ELLIPSIS)] + ELLIPSIS


def humanize_value(value: str) -> str:
    return value.replace("_", " ").capitalize()


def label_executor(executor: str) -> str:
    return CHAT_EXECUTOR_LABELS.get(executor, humanize_value(executor))
