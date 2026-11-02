from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.test_cases.domains.review_comment.entity import ReviewComment
from app.modules.test_cases.domains.review_comment_view.entity import ReviewCommentView


class ReviewCommentRepository(ABC):
    @abstractmethod
    async def find_for_update(self, test_case_id: UUID, comment_id: UUID) -> ReviewComment | None: ...

    @abstractmethod
    async def find_view(self, comment_id: UUID) -> ReviewCommentView | None: ...

    @abstractmethod
    async def list_views(self, test_case_id: UUID) -> list[ReviewCommentView]: ...

    @abstractmethod
    async def count_open(self, test_case_id: UUID) -> int: ...

    @abstractmethod
    async def create(self, comment: ReviewComment) -> None: ...

    @abstractmethod
    async def save(self, comment: ReviewComment) -> None: ...
