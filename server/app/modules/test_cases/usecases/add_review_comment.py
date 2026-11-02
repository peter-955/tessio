from datetime import UTC, datetime
from uuid import uuid7

from app.modules.test_cases.domains.review_comment.entity import ReviewComment
from app.modules.test_cases.domains.review_comment.repository import ReviewCommentRepository
from app.modules.test_cases.domains.review_comment_view.entity import ReviewCommentView
from app.modules.test_cases.domains.test_case.entity import TestCase
from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion
from app.modules.test_cases.domains.test_case_version.repository import TestCaseVersionRepository
from app.modules.test_cases.errors import (
    ReviewCommentNotFoundError,
    ReviewCommentOnDeprecatedCaseError,
    ReviewCommentStepNotFoundError,
    TestCaseVersionNotFoundError,
)
from app.modules.test_cases.utils.review_comment_event import build_review_comment_changed_event
from app.modules.test_cases.utils.test_case_lookup import require_current_version, require_locked_test_case
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class AddReviewCommentUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_case_repository: TestCaseRepository,
        test_case_version_repository: TestCaseVersionRepository,
        review_comment_repository: ReviewCommentRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_case_repository = test_case_repository
        self._test_case_version_repository = test_case_version_repository
        self._review_comment_repository = review_comment_repository
        self._live_event_publisher = live_event_publisher

    async def execute(
        self,
        actor: Actor,
        project_key: str,
        case_code: str,
        body: str,
        step_order: int | None,
        version_number: int | None,
    ) -> ReviewCommentView:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_EDIT)
            test_case = await require_locked_test_case(self._test_case_repository, access.project_id, case_code)
            if test_case.is_deprecated:
                raise ReviewCommentOnDeprecatedCaseError
            version = await self._find_version(test_case, version_number)
            if step_order is not None and all(step.order != step_order for step in version.steps):
                raise ReviewCommentStepNotFoundError
            comment = ReviewComment(
                id=uuid7(),
                test_case_id=test_case.id,
                version_id=version.id,
                step_order=step_order,
                body=body.strip(),
                author_id=actor.user_id,
                created_at=datetime.now(UTC),
                resolved_at=None,
                resolved_by=None,
            )
            await self._review_comment_repository.create(comment)
            view = await self._review_comment_repository.find_view(comment.id)
            if view is None:
                raise ReviewCommentNotFoundError
        await self._live_event_publisher.publish(build_review_comment_changed_event(test_case, comment))
        return view

    async def _find_version(self, test_case: TestCase, version_number: int | None) -> TestCaseVersion:
        if version_number is None:
            return await require_current_version(self._test_case_version_repository, test_case)
        versions = await self._test_case_version_repository.list_for_case(test_case.id)
        for version in versions:
            if version.number == version_number:
                return version
        raise TestCaseVersionNotFoundError
