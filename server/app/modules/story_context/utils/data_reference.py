from app.modules.story_context.typing.constants import DATA_REFERENCE_PREFIX, REFERENCE_SUFFIX


def build_data_reference(key: str) -> str:
    return f"{DATA_REFERENCE_PREFIX}{key}{REFERENCE_SUFFIX}"
