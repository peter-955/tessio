from app.modules.files.typing.constants.file_name import (
    FALLBACK_FILE_NAME,
    MAX_FILE_NAME_LENGTH,
    UNSAFE_FILE_NAME_CHARACTERS,
)


def sanitize_file_name(file_name: str) -> str:
    sanitized_name = UNSAFE_FILE_NAME_CHARACTERS.sub("-", file_name)[:MAX_FILE_NAME_LENGTH]
    return FALLBACK_FILE_NAME if not sanitized_name.strip(".") else sanitized_name
