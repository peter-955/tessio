import json

import yaml

from app.modules.test_data.domains.import_skip.entity import ImportSkip
from app.modules.test_data.domains.parsed_import.entity import ParsedImport
from app.modules.test_data.errors import ImportInvalidFileError
from app.modules.test_data.typing.constants import (
    DOTENV_FILE_NAME,
    JSON_FILE_EXTENSIONS,
    MAX_DATA_ITEM_VALUE_LENGTH,
    MAX_IMPORT_ITEMS,
    YAML_FILE_EXTENSIONS,
)
from app.modules.test_data.typing.enums import ImportFormat, ImportSkipReason
from app.modules.test_data.utils.dotenv_parser import parse_dotenv
from app.modules.test_data.utils.mapping_import_parser import parse_mapping
from app.shared.typing.constants import NUL_CHARACTER


def detect_import_format(file_name: str) -> ImportFormat:
    base_name = file_name.replace("\\", "/").rsplit("/", 1)[-1].strip().lower()
    if base_name.endswith(DOTENV_FILE_NAME) or base_name.startswith(f"{DOTENV_FILE_NAME}."):
        return ImportFormat.DOTENV
    if base_name.endswith(JSON_FILE_EXTENSIONS):
        return ImportFormat.JSON
    if base_name.endswith(YAML_FILE_EXTENSIONS):
        return ImportFormat.YAML
    raise ImportInvalidFileError


def parse_import_file(file_name: str, content: bytes) -> ParsedImport:
    import_format = detect_import_format(file_name)
    try:
        text = content.decode("utf-8-sig").replace(NUL_CHARACTER, "")
    except UnicodeDecodeError as error:
        raise ImportInvalidFileError from error
    parsed_import = parse_text(text, import_format)
    entries = []
    skipped = list(parsed_import.skipped)
    for entry in parsed_import.entries:
        if not entry.value:
            skipped.append(ImportSkip(location=entry.key, reason=ImportSkipReason.UNSUPPORTED_VALUE))
        elif len(entry.value) > MAX_DATA_ITEM_VALUE_LENGTH:
            skipped.append(ImportSkip(location=entry.key, reason=ImportSkipReason.VALUE_TOO_LONG))
        else:
            entries.append(entry)
    if len(entries) > MAX_IMPORT_ITEMS:
        raise ImportInvalidFileError
    return ParsedImport(format=import_format, entries=entries, skipped=skipped)


def parse_text(text: str, import_format: ImportFormat) -> ParsedImport:
    if import_format is ImportFormat.DOTENV:
        return parse_dotenv(text)
    try:
        data: object = json.loads(text) if import_format is ImportFormat.JSON else yaml.safe_load(text)
    except (ValueError, yaml.YAMLError) as error:
        raise ImportInvalidFileError from error
    return parse_mapping(data, import_format)
