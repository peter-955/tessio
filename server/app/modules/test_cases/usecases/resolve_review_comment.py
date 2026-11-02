from datetime import UTC, datetime
from uuid import UUID

from app.modules.test_cases.domains.review_comment.repository import ReviewCommentRepository
from app.modules.test_cases.domains.review_comment_view.entity import ReviewCommentView
from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.errors import ReviewCommentNotFoundError
from app.modules.test_cases.utils.review_comment_event import build_review_comment_changed_event
from app.modules.test_cases.utils.test_case_lookup import require_test_case
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ResolveReviewCommentUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_case_repository: TestCaseRepository,
        review_comment_repository: ReviewCommentRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_case_repository = test_case_repository
        self._review_comment_repository = review_comment_repository
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, case_code: str, comment_id: UUID) -> ReviewCommentView:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_EDIT)
            test_case = await require_test_case(self._test_case_repository, access.project_id, case_code)
            comment = await self._review_comment_repository.find_for_update(test_case.id, comment_id)
            if comment is None:
                raise ReviewCommentNotFoundError
            is_changing = not comment.is_resolved
            if is_changing:
                comment = comment.model_copy(update={"resolved_at": datetime.now(UTC), "resolved_by": actor.user_id})
                await self._review_comment_repository.save(comment)
            view = await self._review_comment_repository.find_view(comment.id)
            if view is None:
                raise ReviewCommentNotFoundError
        if is_changing:
            await self._live_event_publisher.publish(build_review_comment_changed_event(test_case, comment))
        return view
