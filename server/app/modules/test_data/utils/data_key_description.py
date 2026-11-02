from uuid import UUID

from app.modules.test_data.domains.data_item.repository import DataItemRepository
from app.modules.test_data.domains.data_key_description.repository import DataKeyDescriptionRepository


async def apply_key_description(
    description_repository: DataKeyDescriptionRepository, project_id: UUID, key: str, description: str | None
) -> str | None:
    if description is None:
        return await description_repository.find(project_id, key)
    cleaned_description = description.strip()
    if not cleaned_description:
        await description_repository.delete(project_id, key)
        return None
    await description_repository.save(project_id, key, cleaned_description)
    return cleaned_description


async def remove_unused_key_description(
    data_item_repository: DataItemRepository,
    description_repository: DataKeyDescriptionRepository,
    project_id: UUID,
    key: str,
) -> None:
    if await data_item_repository.count_by_key(project_id, key) == 0:
        await description_repository.delete(project_id, key)
