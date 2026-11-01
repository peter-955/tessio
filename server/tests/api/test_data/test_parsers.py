import json

import pytest

from app.modules.test_data.domains.import_entry.entity import ImportEntry
from app.modules.test_data.domains.import_skip.entity import ImportSkip
from app.modules.test_data.errors import ImportInvalidFileError
from app.modules.test_data.typing.enums import DataItemKind, ImportFormat, ImportSkipReason
from app.modules.test_data.utils.dotenv_parser import parse_dotenv
from app.modules.test_data.utils.import_file_parser import detect_import_format, parse_import_file
from app.modules.test_data.utils.mapping_import_parser import parse_mapping
from app.modules.test_data.utils.suggested_kind import suggest_kind


def entries_of(*pairs: tuple[str, str]) -> list[ImportEntry]:
    return [ImportEntry(key=key, value=value) for key, value in pairs]


def test_dotenv_skips_blank_lines_and_comments_and_strips_export() -> None:
    parsed = parse_dotenv("\n# a comment\n   # indented comment\nexport BASE_URL=https://shop.test\nUSER=alice\n")

    assert parsed.format is ImportFormat.DOTENV
    assert parsed.entries == entries_of(("BASE_URL", "https://shop.test"), ("USER", "alice"))
    assert parsed.skipped == []


def test_dotenv_double_quotes_unescape_newlines_tabs_quotes_and_backslashes() -> None:
    parsed = parse_dotenv('GREETING="line one\\nline\\ttwo \\"quoted\\" back\\\\slash # not a comment"\n')

    assert parsed.entries == entries_of(("GREETING", 'line one\nline\ttwo "quoted" back\\slash # not a comment'))


def test_dotenv_single_quotes_keep_the_content_literally() -> None:
    parsed = parse_dotenv("PATTERN='a\\nb \"c\" # d'  # trailing comment\n")

    assert parsed.entries == entries_of(("PATTERN", 'a\\nb "c" # d'))


def test_dotenv_unquoted_values_are_cut_at_an_inline_comment_and_stripped() -> None:
    parsed = parse_dotenv("TIMEOUT =  30   # seconds\nCOLOR=#fff\nURL=https://shop.test/#anchor\n")

    assert parsed.entries == entries_of(("TIMEOUT", "30"), ("COLOR", "#fff"), ("URL", "https://shop.test/#anchor"))


def test_dotenv_value_keeps_everything_after_the_first_equals_sign() -> None:
    parsed = parse_dotenv("QUERY=a=b&c=d\n")

    assert parsed.entries == entries_of(("QUERY", "a=b&c=d"))


def test_dotenv_line_without_equals_is_an_invalid_line() -> None:
    parsed = parse_dotenv("GOOD=1\njust some text\nALSO_GOOD=2\n")

    assert parsed.entries == entries_of(("GOOD", "1"), ("ALSO_GOOD", "2"))
    assert parsed.skipped == [ImportSkip(location="2", reason=ImportSkipReason.INVALID_LINE)]


def test_dotenv_unterminated_quote_is_an_invalid_line() -> None:
    parsed = parse_dotenv("OPEN=\"no end\nSINGLE='no end\n")

    assert parsed.entries == []
    assert parsed.skipped == [
        ImportSkip(location="1", reason=ImportSkipReason.INVALID_LINE),
        ImportSkip(location="2", reason=ImportSkipReason.INVALID_LINE),
    ]


def test_dotenv_bad_key_is_an_invalid_key() -> None:
    parsed = parse_dotenv("1ST=one\nHAS SPACE=two\n=empty\nOK_KEY=three\n")

    assert parsed.entries == entries_of(("OK_KEY", "three"))
    assert parsed.skipped == [
        ImportSkip(location="1", reason=ImportSkipReason.INVALID_KEY),
        ImportSkip(location="2", reason=ImportSkipReason.INVALID_KEY),
        ImportSkip(location="3", reason=ImportSkipReason.INVALID_KEY),
    ]


def test_dotenv_duplicate_key_keeps_the_last_value() -> None:
    parsed = parse_dotenv("USER=alice\nOTHER=x\nUSER=bob\n")

    assert parsed.entries == entries_of(("USER", "bob"), ("OTHER", "x"))


def test_json_nested_mappings_flatten_with_dots_and_scalars_become_text() -> None:
    data = json.loads(
        '{"admin": {"password": "x", "profile": {"age": 41}}, "ratio": 1.5, "enabled": true, "off": false,'
        ' "nothing": null, "items": [1, 2], "bad key": "v"}'
    )

    parsed = parse_mapping(data, ImportFormat.JSON)

    assert parsed.format is ImportFormat.JSON
    assert parsed.entries == entries_of(
        ("admin.password", "x"), ("admin.profile.age", "41"), ("ratio", "1.5"), ("enabled", "true"), ("off", "false")
    )
    assert parsed.skipped == [
        ImportSkip(location="nothing", reason=ImportSkipReason.UNSUPPORTED_VALUE),
        ImportSkip(location="items", reason=ImportSkipReason.UNSUPPORTED_VALUE),
        ImportSkip(location="bad key", reason=ImportSkipReason.INVALID_KEY),
    ]


@pytest.mark.parametrize("data", [[1, 2], "text", 3, None])
def test_mapping_parser_needs_a_top_level_mapping(data: object) -> None:
    with pytest.raises(ImportInvalidFileError):
        parse_mapping(data, ImportFormat.JSON)


def test_yaml_file_is_parsed_and_flattened() -> None:
    content = b"base_url: https://shop.test\nadmin:\n  user: alice\n  password: 's3cret'\nretries: 3\ndebug: yes\n"

    parsed = parse_import_file("staging.yaml", content)

    assert parsed.format is ImportFormat.YAML
    assert parsed.entries == entries_of(
        ("base_url", "https://shop.test"),
        ("admin.user", "alice"),
        ("admin.password", "s3cret"),
        ("retries", "3"),
        ("debug", "true"),
    )


def test_json_file_with_a_byte_order_mark_is_parsed() -> None:
    parsed = parse_import_file("data.json", '﻿{"USER": "alice"}'.encode())

    assert parsed.entries == entries_of(("USER", "alice"))


def test_nul_characters_are_stripped_from_an_import_file() -> None:
    parsed = parse_import_file(".env", b"US\x00ER=ali\x00ce\n")

    assert parsed.entries == entries_of(("USER", "alice"))


@pytest.mark.parametrize(
    ("file_name", "content"),
    [
        ("list.json", b"[1, 2]"),
        ("list.yaml", b"- a\n- b\n"),
        ("empty.yaml", b""),
        ("broken.json", b"{not json"),
        ("broken.yml", b"key: [unclosed"),
        ("binary.env", b"\xff\xfe\x00"),
        ("notes.txt", b"USER=alice"),
        ("archive.zip", b"PK"),
    ],
)
def test_invalid_files_are_refused(file_name: str, content: bytes) -> None:
    with pytest.raises(ImportInvalidFileError):
        parse_import_file(file_name, content)


@pytest.mark.parametrize(
    ("file_name", "import_format"),
    [
        (".env", ImportFormat.DOTENV),
        ("staging.env", ImportFormat.DOTENV),
        (".env.local", ImportFormat.DOTENV),
        ("folder/.ENV.Production", ImportFormat.DOTENV),
        ("data.JSON", ImportFormat.JSON),
        ("data.yaml", ImportFormat.YAML),
        ("data.yml", ImportFormat.YAML),
    ],
)
def test_format_is_detected_from_the_file_name(file_name: str, import_format: ImportFormat) -> None:
    assert detect_import_format(file_name) is import_format


def test_too_long_and_empty_values_are_skipped() -> None:
    content = f"LONG={'x' * 10001}\nEMPTY=\nOK=fine\n".encode()

    parsed = parse_import_file(".env", content)

    assert parsed.entries == entries_of(("OK", "fine"))
    assert parsed.skipped == [
        ImportSkip(location="LONG", reason=ImportSkipReason.VALUE_TOO_LONG),
        ImportSkip(location="EMPTY", reason=ImportSkipReason.UNSUPPORTED_VALUE),
    ]


def test_more_than_one_thousand_entries_are_refused() -> None:
    content = "\n".join(f"KEY_{index}=value" for index in range(1001)).encode()

    with pytest.raises(ImportInvalidFileError):
        parse_import_file(".env", content)


@pytest.mark.parametrize(
    ("key", "value", "kind"),
    [
        ("ADMIN_PASSWORD", "x", DataItemKind.SECRET),
        ("db.passwd", "x", DataItemKind.SECRET),
        ("PWD", "x", DataItemKind.SECRET),
        ("client_secret", "x", DataItemKind.SECRET),
        ("ACCESS_TOKEN", "https://not-an-endpoint.test", DataItemKind.SECRET),
        ("stripe.api-key", "x", DataItemKind.SECRET),
        ("PRIVATE_KEY", "x", DataItemKind.SECRET),
        ("aws_credentials", "x", DataItemKind.SECRET),
        ("CHECKOUT_URL", "https://shop.test/checkout", DataItemKind.ENDPOINT),
        ("LEGACY", "http://old.test", DataItemKind.ENDPOINT),
        ("USER", "alice", DataItemKind.VARIABLE),
        ("NOTE", "see https://shop.test", DataItemKind.VARIABLE),
    ],
)
def test_suggest_kind(key: str, value: str, kind: DataItemKind) -> None:
    assert suggest_kind(key, value) is kind
