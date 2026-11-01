from collections.abc import Iterable
from uuid import UUID

from app.modules.story_context.domains.data_entry.entity import DataEntry


def select_effective_entries(entries: Iterable[DataEntry], environment_id: UUID | None) -> list[DataEntry]:
    effective_by_key: dict[str, DataEntry] = {}
    for entry in entries:
        if entry.environment_id is None:
            effective_by_key.setdefault(entry.key, entry)
        elif environment_id is not None and entry.environment_id == environment_id:
            effective_by_key[entry.key] = entry
    return sorted(effective_by_key.values(), key=lambda entry: entry.key)
