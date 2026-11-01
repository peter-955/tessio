from uuid import UUID

from app.modules.projects.utils.effective_role import is_acting_as_workspace_admin
from app.shared.permissions import Actor


def select_visible_project_ids(actor: Actor, member_project_ids: frozenset[UUID]) -> frozenset[UUID] | None:
    visible_project_ids = None if is_acting_as_workspace_admin(actor) else member_project_ids
    if actor.token_project_id is None:
        return visible_project_ids
    if visible_project_ids is None:
        return frozenset({actor.token_project_id})
    return visible_project_ids & {actor.token_project_id}
