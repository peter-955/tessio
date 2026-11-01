def normalize_content_type(content_type: str) -> str:
    return content_type.partition(";")[0].strip().lower()
