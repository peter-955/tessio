import uuid
from datetime import UTC, datetime
from uuid import UUID, uuid7

import pytest

from app.container import Container
from app.modules.projects import Project, ProjectMember
from app.modules.projects.infrastructure import (
    PostgresProjectAccessResolver,
    PostgresProjectMemberRepository,
    PostgresProjectRepository,
)
from app.modules.users import User, UserStatus
from app.modules.users import WorkspaceRole as UserWorkspaceRole
from app.shared.permissions import Actor, ProjectNotFoundError, ProjectRole, WorkspaceRole


async def create_user(container: Container, workspace_role: UserWorkspaceRole) -> UUID:
    user = User(
        id=uuid7(),
        email=f"user-{uuid.uuid4().hex[:8]}@tessio.test",
        name="Resolver User",
        workspace_role=workspace_role,
        status=UserStatus.ACTIVE,
        password_hash=None,
        totp_key_encrypted=None,
        totp_confirmed_at=None,
        totp_last_time_step=None,
        failed_sign_ins=0,
        locked_until=None,
        created_at=datetime.now(UTC),
    )
    async with container.database.begin():
        await container.user_repository.add(user)
    return user.id


async def create_project(container: Container, member_id: UUID, role: ProjectRole) -> Project:
    now = datetime.now(UTC)
    suffix = uuid.uuid4().hex[:6].upper()
    project = Project(
        id=uuid7(),
        key=f"R{suffix}",
        name=f"Resolver {suffix}",
        description=None,
        jira_project_key=f"J{suffix}",
        jira_board_id=1,
        allowed_file_types=["image/png"],
        archived_at=None,
        created_at=now,
    )
    async with container.database.begin():
        await PostgresProjectRepository(container.database).save(project)
        await PostgresProjectMemberRepository(container.database).save(
            ProjectMember(id=uuid7(), project_id=project.id, user_id=member_id, role=role, created_at=now)
        )
    return project


@pytest.fixture
def resolver(container: Container) -> PostgresProjectAccessResolver:
    return PostgresProjectAccessResolver(container.database)


async def test_member_gets_their_role(container: Container, resolver: PostgresProjectAccessResolver) -> None:
    member_id = await create_user(container, UserWorkspaceRole.MEMBER)
    project = await create_project(container, member_id, ProjectRole.QC)

    async with container.database.begin():
        by_key = await resolver.resolve(Actor(user_id=member_id, workspace_role=WorkspaceRole.MEMBER), project.key)
        by_id = await resolver.resolve_by_id(Actor(user_id=member_id, workspace_role=WorkspaceRole.MEMBER), project.id)

    assert by_key.role is ProjectRole.QC
    assert by_key.project_id == project.id
    assert by_key.is_archived is False
    assert by_id == by_key


async def test_non_member_gets_no_role(container: Container, resolver: PostgresProjectAccessResolver) -> None:
    member_id = await create_user(container, UserWorkspaceRole.MEMBER)
    outsider_id = await create_user(container, UserWorkspaceRole.MEMBER)
    project = await create_project(container, member_id, ProjectRole.ADMIN)

    async with container.database.begin():
        access = await resolver.resolve(Actor(user_id=outsider_id, workspace_role=WorkspaceRole.MEMBER), project.key)

    assert access.role is None


async def test_workspace_admin_acts_as_project_admin(
    container: Container, resolver: PostgresProjectAccessResolver
) -> None:
    member_id = await create_user(container, UserWorkspaceRole.MEMBER)
    admin_id = await create_user(container, UserWorkspaceRole.ADMIN)
    project = await create_project(container, member_id, ProjectRole.ADMIN)

    async with container.database.begin():
        access = await resolver.resolve(Actor(user_id=admin_id, workspace_role=WorkspaceRole.ADMIN), project.key)

    assert access.role is ProjectRole.ADMIN


async def test_workspace_admin_with_a_lower_membership_still_acts_as_project_admin(
    container: Container, resolver: PostgresProjectAccessResolver
) -> None:
    admin_id = await create_user(container, UserWorkspaceRole.ADMIN)
    project = await create_project(container, admin_id, ProjectRole.VIEWER)
    session_actor = Actor(user_id=admin_id, workspace_role=WorkspaceRole.ADMIN)
    token_actor = Actor(user_id=admin_id, workspace_role=WorkspaceRole.ADMIN, api_token_id=uuid7())

    async with container.database.begin():
        session_access = await resolver.resolve(session_actor, project.key)
        token_access = await resolver.resolve(token_actor, project.key)

    assert session_access.role is ProjectRole.ADMIN
    assert token_access.role is ProjectRole.VIEWER


async def test_workspace_admin_token_actor_gets_only_real_membership(
    container: Container, resolver: PostgresProjectAccessResolver
) -> None:
    member_id = await create_user(container, UserWorkspaceRole.MEMBER)
    owner_id = await create_user(container, UserWorkspaceRole.OWNER)
    project = await create_project(container, member_id, ProjectRole.ADMIN)
    token_actor = Actor(user_id=owner_id, workspace_role=WorkspaceRole.OWNER, api_token_id=uuid7())

    async with container.database.begin():
        access = await resolver.resolve(token_actor, project.key)

    assert access.role is None


async def test_token_for_another_project_hides_the_project(
    container: Container, resolver: PostgresProjectAccessResolver
) -> None:
    member_id = await create_user(container, UserWorkspaceRole.MEMBER)
    project = await create_project(container, member_id, ProjectRole.DEV)
    other_project = await create_project(container, member_id, ProjectRole.DEV)
    token_actor = Actor(
        user_id=member_id,
        workspace_role=WorkspaceRole.MEMBER,
        api_token_id=uuid7(),
        token_project_id=other_project.id,
    )

    async with container.database.begin():
        with pytest.raises(ProjectNotFoundError):
            await resolver.resolve(token_actor, project.key)
        access = await resolver.resolve(token_actor, other_project.key)

    assert access.role is ProjectRole.DEV


async def test_unknown_project_is_not_found(container: Container, resolver: PostgresProjectAccessResolver) -> None:
    actor = Actor(user_id=uuid7(), workspace_role=WorkspaceRole.OWNER)

    async with container.database.begin():
        with pytest.raises(ProjectNotFoundError):
            await resolver.resolve(actor, "NOPE404")
        with pytest.raises(ProjectNotFoundError):
            await resolver.resolve_by_id(actor, uuid7())


async def test_visible_project_ids(container: Container, resolver: PostgresProjectAccessResolver) -> None:
    member_id = await create_user(container, UserWorkspaceRole.MEMBER)
    admin_id = await create_user(container, UserWorkspaceRole.ADMIN)
    member_project = await create_project(container, member_id, ProjectRole.VIEWER)
    admin_project = await create_project(container, admin_id, ProjectRole.ADMIN)
    member_actor = Actor(user_id=member_id, workspace_role=WorkspaceRole.MEMBER)
    admin_actor = Actor(user_id=admin_id, workspace_role=WorkspaceRole.ADMIN)
    admin_token_actor = Actor(user_id=admin_id, workspace_role=WorkspaceRole.ADMIN, api_token_id=uuid7())
    scoped_actor = Actor(
        user_id=member_id,
        workspace_role=WorkspaceRole.MEMBER,
        api_token_id=uuid7(),
        token_project_id=admin_project.id,
    )

    async with container.database.begin():
        member_visible = await resolver.list_visible_project_ids(member_actor)
        admin_visible = await resolver.list_visible_project_ids(admin_actor)
        admin_token_visible = await resolver.list_visible_project_ids(admin_token_actor)
        scoped_visible = await resolver.list_visible_project_ids(scoped_actor)

    assert member_visible == {member_project.id}
    assert {member_project.id, admin_project.id} <= admin_visible
    assert admin_token_visible == {admin_project.id}
    assert scoped_visible == frozenset()
