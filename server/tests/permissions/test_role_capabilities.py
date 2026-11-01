from uuid import uuid4

import pytest

from app.shared.permissions import (
    READ_CAPABILITIES,
    Actor,
    Capability,
    PermissionDeniedError,
    ProjectAccess,
    ProjectArchivedError,
    ProjectNotFoundError,
    ProjectRole,
    WorkspaceCapability,
    WorkspaceRole,
    has_capability,
    list_capabilities,
    require,
    require_workspace,
)

VIEWS = {
    "project.view",
    "sprint.view",
    "story.view",
    "test_case.view",
    "test_data.view",
    "gap.view",
    "run.view",
    "report.view",
    "failure.view",
    "file.download",
}
EVERY_ROLE = VIEWS | {"api_token.create"}
GAPS = {"gap.raise", "gap.answer", "gap.reassign"}

EXPECTED: dict[ProjectRole, set[str]] = {
    ProjectRole.ADMIN: VIEWS
    | GAPS
    | {
        "api_token.create",
        "project.edit",
        "member.manage",
        "jira.sync",
        "story.mark_ready_for_test",
        "story.sign_off",
        "test_case.edit",
        "environment.manage",
        "test_data.edit",
        "secret.edit",
        "secret.reveal",
        "secret.use_in_run",
        "run.start",
        "run.record_manual",
        "run.finish_any",
        "failure.assign",
        "failure.mark_fixed",
        "failure.verify",
    },
    ProjectRole.PM: EVERY_ROLE | GAPS | {"jira.sync"},
    ProjectRole.BA: EVERY_ROLE | GAPS | {"jira.sync"},
    ProjectRole.QC: EVERY_ROLE
    | GAPS
    | {
        "story.sign_off",
        "test_case.edit",
        "environment.manage",
        "test_data.edit",
        "secret.edit",
        "secret.reveal",
        "secret.use_in_run",
        "run.start",
        "run.record_manual",
        "failure.assign",
        "failure.verify",
    },
    ProjectRole.DEV: EVERY_ROLE
    | GAPS
    | {
        "story.mark_ready_for_test",
        "environment.manage",
        "test_data.edit",
        "secret.use_in_run",
        "run.start",
        "failure.assign",
        "failure.mark_fixed",
    },
    ProjectRole.VIEWER: EVERY_ROLE,
}

EXPECTED_WORKSPACE: dict[WorkspaceRole, set[str]] = {
    WorkspaceRole.OWNER: {
        "user.manage",
        "project.create",
        "project.archive",
        "project.view_all",
        "jira.configure",
        "user_access.view",
        "workspace_role.manage",
    },
    WorkspaceRole.ADMIN: {
        "user.manage",
        "project.create",
        "project.archive",
        "project.view_all",
        "jira.configure",
        "user_access.view",
    },
    WorkspaceRole.MEMBER: set(),
}

ROLE_CAPABILITY_PAIRS = [(role, capability) for role in ProjectRole for capability in Capability]
WORKSPACE_PAIRS = [(role, capability) for role in WorkspaceRole for capability in WorkspaceCapability]


def build_access(role: ProjectRole | None, is_archived: bool = False) -> ProjectAccess:
    return ProjectAccess(project_id=uuid4(), project_key="TES", role=role, is_archived=is_archived)


def test_expected_table_names_only_existing_capabilities() -> None:
    known_values = {capability.value for capability in Capability}
    assert all(values <= known_values for values in EXPECTED.values())
    assert EXPECTED[ProjectRole.ADMIN] == known_values


@pytest.mark.parametrize(("role", "capability"), ROLE_CAPABILITY_PAIRS)
def test_role_has_exactly_the_expected_capabilities(role: ProjectRole, capability: Capability) -> None:
    is_expected = capability.value in EXPECTED[role]

    assert has_capability(build_access(role), capability) is is_expected


@pytest.mark.parametrize(("role", "capability"), ROLE_CAPABILITY_PAIRS)
def test_require_refuses_exactly_the_unexpected_capabilities(role: ProjectRole, capability: Capability) -> None:
    if capability.value in EXPECTED[role]:
        require(build_access(role), capability)
    else:
        with pytest.raises(PermissionDeniedError):
            require(build_access(role), capability)


@pytest.mark.parametrize("capability", list(Capability))
def test_no_role_hides_the_project(capability: Capability) -> None:
    with pytest.raises(ProjectNotFoundError):
        require(build_access(None), capability)
    assert has_capability(build_access(None), capability) is False


@pytest.mark.parametrize("capability", list(Capability))
def test_archived_project_allows_reads_and_refuses_writes(capability: Capability) -> None:
    access = build_access(ProjectRole.ADMIN, is_archived=True)
    is_read = capability.value in VIEWS | {"secret.reveal"}

    if is_read:
        require(access, capability)
    else:
        with pytest.raises(ProjectArchivedError):
            require(access, capability)
    assert has_capability(access, capability) is is_read


def test_archived_project_lists_only_read_capabilities() -> None:
    assert {capability.value for capability in list_capabilities(build_access(ProjectRole.ADMIN, True))} == VIEWS | {
        "secret.reveal"
    }
    assert {capability.value for capability in list_capabilities(build_access(ProjectRole.VIEWER, True))} == VIEWS


def test_missing_role_lists_no_capabilities() -> None:
    assert list_capabilities(build_access(None)) == frozenset()


def test_member_without_capability_on_archived_project_is_denied_not_archived() -> None:
    with pytest.raises(PermissionDeniedError):
        require(build_access(ProjectRole.VIEWER, is_archived=True), Capability.PROJECT_EDIT)


@pytest.mark.parametrize(("workspace_role", "capability"), WORKSPACE_PAIRS)
def test_workspace_role_has_exactly_the_expected_capabilities(
    workspace_role: WorkspaceRole, capability: WorkspaceCapability
) -> None:
    actor = Actor(user_id=uuid4(), workspace_role=workspace_role)

    if capability.value in EXPECTED_WORKSPACE[workspace_role]:
        require_workspace(actor, capability)
    else:
        with pytest.raises(PermissionDeniedError):
            require_workspace(actor, capability)


def test_viewer_has_nothing_beyond_reads_and_api_tokens() -> None:
    viewer_capabilities = list_capabilities(build_access(ProjectRole.VIEWER))

    assert viewer_capabilities <= READ_CAPABILITIES | {Capability.API_TOKEN_CREATE}
