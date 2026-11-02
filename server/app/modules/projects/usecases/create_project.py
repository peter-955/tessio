from datetime import UTC, datetime
from uuid import uuid7

from app.modules.projects.domains.project.entity import Project
from app.modules.projects.domains.project.repository import ProjectRepository
from app.modules.projects.domains.project_member.entity import ProjectMember
from app.modules.projects.domains.project_member.repository import ProjectMemberRepository
from app.modules.projects.domains.project_overview.entity import ProjectOverview
from app.modules.projects.errors import (
    JiraNotConfiguredError,
    JiraProjectAlreadyLinkedError,
    ProjectKeyAlreadyUsedError,
)
from app.modules.projects.ports.jira_connection_checker import JiraConnectionChecker
from app.modules.projects.typing.constants import DEFAULT_ALLOWED_FILE_TYPES
from app.modules.projects.utils.project_access import build_project_access
from app.shared.common import Transaction
from app.shared.permissions import Actor, ProjectRole, WorkspaceCapability, require_workspace


class CreateProjectUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_repository: ProjectRepository,
        project_member_repository: ProjectMemberRepository,
        jira_connection_checker: JiraConnectionChecker,
    ) -> None:
        self._transaction = transaction
        self._project_repository = project_repository
        self._project_member_repository = project_member_repository
        self._jira_connection_checker = jira_connection_checker

    async def execute(
        self,
        actor: Actor,
        key: str,
        name: str,
        description: str | None,
        jira_project_key: str | None,
        jira_board_id: int | None,
    ) -> ProjectOverview:
        require_workspace(actor, WorkspaceCapability.PROJECT_CREATE)
        cleaned_jira_project_key = None if jira_project_key is None else jira_project_key.strip() or None
        is_linked_to_jira = cleaned_jira_project_key is not None and jira_board_id is not None
        if is_linked_to_jira and not await self._jira_connection_checker.is_configured():
            raise JiraNotConfiguredError
        now = datetime.now(UTC)
        stripped_description = None if description is None else description.strip()
        project = Project(
            id=uuid7(),
            key=key,
            name=name.strip(),
            description=stripped_description or None,
            jira_project_key=cleaned_jira_project_key if is_linked_to_jira else None,
            jira_board_id=jira_board_id if is_linked_to_jira else None,
            allowed_file_types=list(DEFAULT_ALLOWED_FILE_TYPES),
            archived_at=None,
            created_at=now,
        )
        async with self._transaction.begin():
            if await self._project_repository.find_by_key(project.key) is not None:
                raise ProjectKeyAlreadyUsedError
            if (
                project.jira_project_key is not None
                and await self._project_repository.find_by_jira_project_key(project.jira_project_key) is not None
            ):
                raise JiraProjectAlreadyLinkedError
            await self._project_repository.save(project)
            await self._project_member_repository.save(
                ProjectMember(
                    id=uuid7(),
                    project_id=project.id,
                    user_id=actor.user_id,
                    role=ProjectRole.ADMIN,
                    created_at=now,
                )
            )
        return ProjectOverview(project=project, access=build_project_access(project, ProjectRole.ADMIN))
