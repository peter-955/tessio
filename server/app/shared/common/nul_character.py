from collections.abc import Mapping

from app.shared.typing.constants import NUL_CHARACTER


def contains_nul_character(value: object) -> bool:
    if isinstance(value, str):
        return NUL_CHARACTER in value
    if isinstance(value, Mapping):
        return any(contains_nul_character(key) or contains_nul_character(item) for key, item in value.items())
    if isinstance(value, list | tuple | set | frozenset):
        return any(contains_nul_character(item) for item in value)
    return False
