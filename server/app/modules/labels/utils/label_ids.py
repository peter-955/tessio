from collections.abc import Sequence
from uuid import UUID

from app.modules.labels.domains.label.entity import Label
from app.modules.labels.domains.label.repository import LabelRepository
from app.modules.labels.errors import LabelNotInProjectError


async def require_project_labels(
    repository: LabelRepository, project_id: UUID, label_ids: Sequence[UUID]
) -> list[Label]:
    requested_ids = frozenset(label_ids)
    labels = await repository.list_by_ids(project_id, requested_ids)
    if len(labels) != len(requested_ids):
        raise LabelNotInProjectError
    return labels
