from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.projects.domains.member_profile.entity import MemberProfile
from app.modules.projects.domains.project.repository import ProjectRepository
from app.modules.projects.domains.project_member.entity import ProjectMember
from app.modules.projects.domains.project_member.repository import ProjectMemberRepository
from app.modules.projects.errors import LastProjectAdminError, UserDeactivatedError, UserNotFoundError
from app.modules.users import UserRepository, UserStatus
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


class SetProjectMemberUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        project_repository: ProjectRepository,
        project_member_repository: ProjectMemberRepository,
        user_repository: UserRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._project_repository = project_repository
        self._project_member_repository = project_member_repository
        self._user_repository = user_repository
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, key: str, user_id: UUID, role: ProjectRole) -> MemberProfile:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, key)
            require(access, Capability.MEMBER_MANAGE)
            project = await self._project_repository.find_by_key_for_update(access.project_key)
            if project is None:
                raise ProjectNotFoundError
            user = await self._user_repository.find_by_id(user_id)
            if user is None:
                raise UserNotFoundError
            if user.status is UserStatus.DEACTIVATED:
                raise UserDeactivatedError
            existing_member = await self._project_member_repository.find(project.id, user_id)
            if (
                existing_member is not None
                and existing_member.role is ProjectRole.ADMIN
                and role is not ProjectRole.ADMIN
                and await self._project_member_repository.count_by_role(project.id, ProjectRole.ADMIN) <= 1
            ):
                raise LastProjectAdminError
            member = (
                ProjectMember(id=uuid7(), project_id=project.id, user_id=user_id, role=role, created_at=now)
                if existing_member is None
                else existing_member.model_copy(update={"role": role})
            )
            await self._project_member_repository.save(member)
        await self._live_event_publisher.publish(
            LiveEvent(type=LiveEventType.PROJECT_MEMBERS_CHANGED, project_id=project.id)
        )
        return MemberProfile(
            user_id=user.id,
            name=user.name,
            email=user.email,
            user_status=user.status,
            role=member.role,
            created_at=member.created_at,
        )
