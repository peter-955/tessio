from collections.abc import Iterable
from uuid import UUID

from app.modules.test_data.domains.data_item.entity import DataItem


def select_effective_items(items: Iterable[DataItem], environment_id: UUID | None) -> list[DataItem]:
    effective_by_key: dict[str, DataItem] = {}
    for item in items:
        if item.environment_id is None:
            effective_by_key.setdefault(item.key, item)
        elif environment_id is not None and item.environment_id == environment_id:
            effective_by_key[item.key] = item
    return sorted(effective_by_key.values(), key=lambda item: item.key)
