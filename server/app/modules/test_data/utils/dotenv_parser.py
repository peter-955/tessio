from app.modules.test_data.domains.import_entry.entity import ImportEntry
from app.modules.test_data.domains.import_skip.entity import ImportSkip
from app.modules.test_data.domains.parsed_import.entity import ParsedImport
from app.modules.test_data.typing.constants import (
    DOTENV_COMMENT_MARKER,
    DOTENV_DOUBLE_QUOTE,
    DOTENV_ESCAPE_CHARACTER,
    DOTENV_EXPORT_PREFIX,
    DOTENV_INLINE_COMMENT_MARKER,
    DOTENV_SINGLE_QUOTE,
    DOTENV_UNESCAPED_BY_CHARACTER,
)
from app.modules.test_data.typing.enums import ImportFormat, ImportSkipReason
from app.modules.test_data.utils.data_item_key import is_valid_data_item_key


def parse_dotenv(text: str) -> ParsedImport:
    value_by_key: dict[str, str] = {}
    skipped: list[ImportSkip] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith(DOTENV_COMMENT_MARKER):
            continue
        if stripped_line.startswith(DOTENV_EXPORT_PREFIX):
            stripped_line = stripped_line.removeprefix(DOTENV_EXPORT_PREFIX).lstrip()
        raw_key, separator, raw_value = stripped_line.partition("=")
        location = str(line_number)
        if not separator:
            skipped.append(ImportSkip(location=location, reason=ImportSkipReason.INVALID_LINE))
            continue
        key = raw_key.strip()
        if not is_valid_data_item_key(key):
            skipped.append(ImportSkip(location=location, reason=ImportSkipReason.INVALID_KEY))
            continue
        value = parse_dotenv_value(raw_value)
        if value is None:
            skipped.append(ImportSkip(location=location, reason=ImportSkipReason.INVALID_LINE))
            continue
        value_by_key[key] = value
    return ParsedImport(
        format=ImportFormat.DOTENV,
        entries=[ImportEntry(key=key, value=value) for key, value in value_by_key.items()],
        skipped=skipped,
    )


def parse_dotenv_value(raw_value: str) -> str | None:
    value = raw_value.lstrip()
    if value.startswith(DOTENV_DOUBLE_QUOTE):
        return parse_double_quoted_value(value)
    if value.startswith(DOTENV_SINGLE_QUOTE):
        return parse_single_quoted_value(value)
    comment_index = raw_value.find(DOTENV_INLINE_COMMENT_MARKER)
    return (raw_value if comment_index == -1 else raw_value[:comment_index]).strip()


def parse_double_quoted_value(value: str) -> str | None:
    characters: list[str] = []
    index = 1
    while index < len(value):
        character = value[index]
        if character == DOTENV_ESCAPE_CHARACTER and index + 1 < len(value):
            next_character = value[index + 1]
            characters.append(DOTENV_UNESCAPED_BY_CHARACTER.get(next_character, character + next_character))
            index += 2
            continue
        if character == DOTENV_DOUBLE_QUOTE:
            return "".join(characters) if is_ignorable_rest(value[index + 1 :]) else None
        characters.append(character)
        index += 1
    return None


def parse_single_quoted_value(value: str) -> str | None:
    closing_index = value.find(DOTENV_SINGLE_QUOTE, 1)
    if closing_index == -1 or not is_ignorable_rest(value[closing_index + 1 :]):
        return None
    return value[1:closing_index]


def is_ignorable_rest(rest: str) -> bool:
    stripped_rest = rest.strip()
    return not stripped_rest or stripped_rest.startswith(DOTENV_COMMENT_MARKER)
