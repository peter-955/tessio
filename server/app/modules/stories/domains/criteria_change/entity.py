from uuid import UUID

from app.shared.common import Entity


class CriteriaChange(Entity):
    project_id: UUID
    story_id: UUID
    added_criterion_ids: frozenset[UUID]
    changed_criterion_ids: frozenset[UUID]
    removed_criterion_ids: frozenset[UUID]

    @property
    def has_changed_or_removed(self) -> bool:
        return bool(self.changed_criterion_ids or self.removed_criterion_ids)
