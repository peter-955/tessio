from app.modules.projects.domains.member_profile.entity import MemberProfile
from app.modules.projects.ports.member_directory import MemberDirectory
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListProjectMembersUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        member_directory: MemberDirectory,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._member_directory = member_directory

    async def execute(self, actor: Actor, key: str) -> list[MemberProfile]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, key)
            require(access, Capability.PROJECT_VIEW)
            return await self._member_directory.list_member_profiles(access.project_id)
