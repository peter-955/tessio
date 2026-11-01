from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.projects.domains.candidate_user.entity import CandidateUser
from app.modules.projects.domains.member_profile.entity import MemberProfile


class MemberDirectory(ABC):
    @abstractmethod
    async def list_member_profiles(self, project_id: UUID) -> list[MemberProfile]: ...

    @abstractmethod
    async def list_candidates(self, project_id: UUID, query: str | None, limit: int) -> list[CandidateUser]: ...
