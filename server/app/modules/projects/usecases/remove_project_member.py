from uuid import UUID

from app.modules.projects.domains.project.repository import ProjectRepository
from app.modules.projects.domains.project_member.repository import ProjectMemberRepository
from app.modules.projects.errors import LastProjectAdminError, ProjectMemberNotFoundError
from app.shared.common import Transaction
from app.shared.events import LiveEvent, LiveEventPublisher, LiveEventType
from app.shared.permissions import (
    Actor,
    Capability,
    ProjectAccessResolver,
    ProjectNotFoundError,
    ProjectRole,
    require,
)


class RemoveProjectMemberUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        project_repository: ProjectRepository,
        project_member_repository: ProjectMemberRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._project_repository = project_repository
        self._project_member_repository = project_member_repository
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, key: str, user_id: UUID) -> None:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, key)
            require(access, Capability.MEMBER_MANAGE)
            project = await self._project_repository.find_by_key_for_update(access.project_key)
            if project is None:
                raise ProjectNotFoundError
            existing_member = await self._project_member_repository.find(project.id, user_id)
            if existing_member is None:
                raise ProjectMemberNotFoundError
            if (
                existing_member.role is ProjectRole.ADMIN
                and await self._project_member_repository.count_by_role(project.id, ProjectRole.ADMIN) <= 1
            ):
                raise LastProjectAdminError
            await self._project_member_repository.delete(project.id, user_id)
        await self._live_event_publisher.publish(
            LiveEvent(type=LiveEventType.PROJECT_MEMBERS_CHANGED, project_id=project.id)
        )
