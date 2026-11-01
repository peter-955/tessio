from app.modules.projects.domains.candidate_user.entity import CandidateUser
from app.modules.projects.ports.member_directory import MemberDirectory
from app.modules.projects.typing.constants import MAX_MEMBER_CANDIDATES
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListMemberCandidatesUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        member_directory: MemberDirectory,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._member_directory = member_directory

    async def execute(self, actor: Actor, key: str, query: str | None) -> list[CandidateUser]:
        stripped_query = None if query is None else query.strip()
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, key)
            require(access, Capability.MEMBER_MANAGE)
            return await self._member_directory.list_candidates(
                access.project_id, stripped_query or None, MAX_MEMBER_CANDIDATES
            )
