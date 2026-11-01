from uuid import uuid4

import pytest

from app.shared.permissions import (
    Capability,
    PermissionDeniedError,
    ProjectAccess,
    ProjectArchivedError,
    ProjectNotFoundError,
    ProjectRole,
    require_any,
)

UPLOAD_CAPABILITIES = (Capability.TEST_CASE_EDIT, Capability.RUN_RECORD_MANUAL, Capability.TEST_DATA_EDIT)


def build_access(role: ProjectRole | None, is_archived: bool = False) -> ProjectAccess:
    return ProjectAccess(project_id=uuid4(), project_key="SHOP", role=role, is_archived=is_archived)


@pytest.mark.parametrize("role", [ProjectRole.ADMIN, ProjectRole.QC, ProjectRole.DEV])
def test_one_held_capability_is_enough(role: ProjectRole) -> None:
    require_any(build_access(role), UPLOAD_CAPABILITIES)


def test_a_role_without_any_of_them_is_denied() -> None:
    with pytest.raises(PermissionDeniedError):
        require_any(build_access(ProjectRole.VIEWER), UPLOAD_CAPABILITIES)


def test_a_non_member_gets_not_found() -> None:
    with pytest.raises(ProjectNotFoundError):
        require_any(build_access(None), UPLOAD_CAPABILITIES)


@pytest.mark.parametrize("role", [ProjectRole.ADMIN, ProjectRole.DEV])
def test_an_archived_project_refuses_write_capabilities(role: ProjectRole) -> None:
    with pytest.raises(ProjectArchivedError):
        require_any(build_access(role, is_archived=True), UPLOAD_CAPABILITIES)


def test_an_archived_project_still_allows_a_read_capability() -> None:
    require_any(build_access(ProjectRole.QC, is_archived=True), (Capability.SECRET_REVEAL, Capability.TEST_DATA_EDIT))
