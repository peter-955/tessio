import json

from pydantic import JsonValue

from app.modules.run_logs.typing.constants import (
    MAX_RUN_LOG_INPUT_LENGTH,
    MAX_RUN_LOG_TEXT_LENGTH,
    TRUNCATED_INPUT_KEY,
)
from app.shared.masking import SecretMasker


def mask_json(value: JsonValue, masker: SecretMasker) -> JsonValue:
    if isinstance(value, str):
        return masker.mask(value)
    if isinstance(value, list):
        return [mask_json(item, masker) for item in value]
    if isinstance(value, dict):
        return {key: mask_json(item, masker) for key, item in value.items()}
    return value


def clean_text(text: str | None, masker: SecretMasker) -> str | None:
    return None if text is None else masker.mask(text)[:MAX_RUN_LOG_TEXT_LENGTH]


def clean_input(value: JsonValue, masker: SecretMasker) -> JsonValue:
    masked = mask_json(value, masker)
    serialized = json.dumps(masked, ensure_ascii=False)
    if len(serialized) <= MAX_RUN_LOG_INPUT_LENGTH:
        return masked
    return {TRUNCATED_INPUT_KEY: serialized[:MAX_RUN_LOG_TEXT_LENGTH]}
