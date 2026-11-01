from app.shared.permissions import Actor, ProjectRole


def is_acting_as_workspace_admin(actor: Actor) -> bool:
    return actor.is_workspace_admin and actor.api_token_id is None


def resolve_effective_role(actor: Actor, member_role: ProjectRole | None) -> ProjectRole | None:
    if is_acting_as_workspace_admin(actor):
        return ProjectRole.ADMIN
    return member_role
