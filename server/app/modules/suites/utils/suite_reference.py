from uuid import UUID


def parse_suite_id(reference: str) -> UUID | None:
    try:
        return UUID(reference.strip())
    except ValueError:
        return None
