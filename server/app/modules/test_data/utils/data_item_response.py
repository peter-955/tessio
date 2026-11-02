from app.modules.test_data.domains.data_item.entity import DataItem
from app.modules.test_data.models.data_item_response import DataItemResponse


def build_data_item_response(item: DataItem) -> DataItemResponse:
    return DataItemResponse(
        id=item.id,
        environment_id=item.environment_id,
        key=item.key,
        kind=item.kind,
        value=None if item.is_secret else item.value,
        has_value=item.value_encrypted is not None if item.is_secret else item.value is not None,
        created_at=item.created_at,
        description=item.description,
    )
