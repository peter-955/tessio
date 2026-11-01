from enum import StrEnum


class DataItemKind(StrEnum):
    VARIABLE = "variable"
    ENDPOINT = "endpoint"
    SECRET = "secret"


class ImportFormat(StrEnum):
    DOTENV = "dotenv"
    JSON = "json"
    YAML = "yaml"


class ImportAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    UNCHANGED = "unchanged"


class ImportSkipReason(StrEnum):
    INVALID_LINE = "invalid_line"
    INVALID_KEY = "invalid_key"
    UNSUPPORTED_VALUE = "unsupported_value"
    VALUE_TOO_LONG = "value_too_long"
