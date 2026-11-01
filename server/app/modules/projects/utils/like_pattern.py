from app.modules.projects.typing.constants.search import LIKE_ESCAPE_CHARACTER


def build_contains_pattern(text: str) -> str:
    escaped = (
        text.replace(LIKE_ESCAPE_CHARACTER, LIKE_ESCAPE_CHARACTER * 2)
        .replace("%", f"{LIKE_ESCAPE_CHARACTER}%")
        .replace("_", f"{LIKE_ESCAPE_CHARACTER}_")
    )
    return f"%{escaped}%"
