from collections.abc import Collection

from app.shared.permissions.actor import Actor
from app.shared.permissions.capability import Capability
from app.shared.permissions.errors import PermissionDeniedError, ProjectArchivedError, ProjectNotFoundError
from app.shared.permissions.project_access import ProjectAccess
from app.shared.permissions.role_capabilities import (
    PROJECT_ROLE_CAPABILITIES,
    READ_CAPABILITIES,
    WORKSPACE_ROLE_CAPABILITIES,
)
from app.shared.permissions.workspace_capability import WorkspaceCapability


def require(access: ProjectAccess, capability: Capability) -> None:
    if access.role is None:
        raise ProjectNotFoundError
    if capability not in PROJECT_ROLE_CAPABILITIES[access.role]:
        raise PermissionDeniedError
    if access.is_archived and capability not in READ_CAPABILITIES:
        raise ProjectArchivedError


def require_any(access: ProjectAccess, capabilities: Collection[Capability]) -> None:
    if access.role is None:
        raise ProjectNotFoundError
    held_capabilities = [
        capability for capability in capabilities if capability in PROJECT_ROLE_CAPABILITIES[access.role]
    ]
    if not held_capabilities:
        raise PermissionDeniedError
    if access.is_archived and all(capability not in READ_CAPABILITIES for capability in held_capabilities):
        raise ProjectArchivedError


def has_capability(access: ProjectAccess, capability: Capability) -> bool:
    return capability in list_capabilities(access)


def list_capabilities(access: ProjectAccess) -> frozenset[Capability]:
    if access.role is None:
        return frozenset()
    role_capabilities = PROJECT_ROLE_CAPABILITIES[access.role]
    return role_capabilities & READ_CAPABILITIES if access.is_archived else role_capabilities


def require_workspace(actor: Actor, capability: WorkspaceCapability) -> None:
    if capability not in WORKSPACE_ROLE_CAPABILITIES[actor.workspace_role]:
        raise PermissionDeniedError
