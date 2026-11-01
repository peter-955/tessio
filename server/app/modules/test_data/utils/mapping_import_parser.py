from collections.abc import Mapping

from app.modules.test_data.domains.import_entry.entity import ImportEntry
from app.modules.test_data.domains.import_skip.entity import ImportSkip
from app.modules.test_data.domains.parsed_import.entity import ParsedImport
from app.modules.test_data.errors import ImportInvalidFileError
from app.modules.test_data.typing.constants import NESTED_KEY_SEPARATOR
from app.modules.test_data.typing.enums import ImportFormat, ImportSkipReason
from app.modules.test_data.utils.data_item_key import is_valid_data_item_key


def parse_mapping(data: object, import_format: ImportFormat) -> ParsedImport:
    if not isinstance(data, Mapping):
        raise ImportInvalidFileError
    value_by_key: dict[str, str] = {}
    skipped: list[ImportSkip] = []
    flatten_mapping(data, "", value_by_key, skipped)
    return ParsedImport(
        format=import_format,
        entries=[ImportEntry(key=key, value=value) for key, value in value_by_key.items()],
        skipped=skipped,
    )


def flatten_mapping(
    mapping: Mapping[object, object], prefix: str, value_by_key: dict[str, str], skipped: list[ImportSkip]
) -> None:
    for raw_key, value in mapping.items():
        key = f"{prefix}{NESTED_KEY_SEPARATOR}{raw_key}" if prefix else str(raw_key)
        if isinstance(value, Mapping):
            flatten_mapping(value, key, value_by_key, skipped)
            continue
        if not is_valid_data_item_key(key):
            skipped.append(ImportSkip(location=key, reason=ImportSkipReason.INVALID_KEY))
            continue
        text_value = convert_scalar(value)
        if text_value is None:
            skipped.append(ImportSkip(location=key, reason=ImportSkipReason.UNSUPPORTED_VALUE))
            continue
        value_by_key[key] = text_value


def convert_scalar(value: object) -> str | None:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str | int | float):
        return str(value)
    return None
