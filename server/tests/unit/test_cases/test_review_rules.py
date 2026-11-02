from datetime import UTC, datetime
from uuid import UUID, uuid7

import pytest

from app.modules.test_cases.domains.review_comment.entity import ReviewComment
from app.modules.test_cases.domains.review_comment.repository import ReviewCommentRepository
from app.modules.test_cases.domains.review_comment_view.entity import ReviewCommentView
from app.modules.test_cases.domains.test_case.entity import TestCase as Case
from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion as CaseVersion
from app.modules.test_cases.errors import ReviewCommentsOpenError, ReviewerIsAuthorError
from app.modules.test_cases.ports.review_policy_reader import ReviewPolicyReader
from app.modules.test_cases.typing.enums import TestCasePriority as CasePriority
from app.modules.test_cases.typing.enums import TestCaseStatus as CaseStatus
from app.modules.test_cases.utils.review_rules import require_no_open_review_comments, require_separate_reviewer
from app.shared.permissions import Actor, WorkspaceRole


class FixedReviewPolicyReader(ReviewPolicyReader):
    def __init__(self, is_requiring: bool) -> None:
        self.is_requiring = is_requiring
        self.read_count = 0

    async def is_requiring_separate_reviewer(self, project_id: UUID) -> bool:
        self.read_count += 1
        return self.is_requiring


class CountingReviewCommentRepository(ReviewCommentRepository):
    def __init__(self, open_count: int) -> None:
        self.open_count = open_count

    async def find_for_update(self, test_case_id: UUID, comment_id: UUID) -> ReviewComment | None:
        return None

    async def find_view(self, comment_id: UUID) -> ReviewCommentView | None:
        return None

    async def list_views(self, test_case_id: UUID) -> list[ReviewCommentView]:
        return []

    async def count_open(self, test_case_id: UUID) -> int:
        return self.open_count

    async def create(self, comment: ReviewComment) -> None:
        return None

    async def save(self, comment: ReviewComment) -> None:
        return None


def build_test_case(author_id: UUID) -> Case:
    return Case(
        id=uuid7(),
        project_id=uuid7(),
        story_id=uuid7(),
        number=1,
        title="Pay by card",
        priority=CasePriority.MEDIUM,
        status=CaseStatus.IN_REVIEW,
        current_version_id=uuid7(),
        status_changed_at=None,
        status_changed_by=None,
        needs_review_at=None,
        needs_review_criterion_ids=[],
        reviewed_at=None,
        reviewed_by=None,
        created_by=author_id,
        created_at=datetime.now(UTC),
    )


def build_version(test_case: Case, author_id: UUID) -> CaseVersion:
    return CaseVersion(
        id=test_case.current_version_id,
        test_case_id=test_case.id,
        number=2,
        title=test_case.title,
        priority=test_case.priority,
        business_value=None,
        preconditions=None,
        steps=[],
        criterion_ids=[],
        data_keys=[],
        file_version_ids=[],
        created_by=author_id,
        created_at=datetime.now(UTC),
    )


def build_actor(user_id: UUID) -> Actor:
    return Actor(user_id=user_id, workspace_role=WorkspaceRole.MEMBER)


async def test_the_author_of_the_version_is_refused_when_the_project_requires_another_reviewer() -> None:
    author_id = uuid7()
    test_case = build_test_case(author_id)

    with pytest.raises(ReviewerIsAuthorError):
        await require_separate_reviewer(
            FixedReviewPolicyReader(True), test_case, build_version(test_case, author_id), build_actor(author_id)
        )


async def test_the_author_passes_when_the_project_allows_self_review() -> None:
    author_id = uuid7()
    test_case = build_test_case(author_id)

    await require_separate_reviewer(
        FixedReviewPolicyReader(False), test_case, build_version(test_case, author_id), build_actor(author_id)
    )


async def test_another_reviewer_passes_without_reading_the_setting() -> None:
    case_author_id = uuid7()
    reviewer_id = uuid7()
    test_case = build_test_case(case_author_id)
    reader = FixedReviewPolicyReader(True)
    version = build_version(test_case, case_author_id)

    await require_separate_reviewer(reader, test_case, version, build_actor(reviewer_id))

    assert reader.read_count == 0


async def test_the_case_creator_passes_when_someone_else_saved_the_current_version() -> None:
    case_author_id = uuid7()
    editor_id = uuid7()
    test_case = build_test_case(case_author_id)

    await require_separate_reviewer(
        FixedReviewPolicyReader(True), test_case, build_version(test_case, editor_id), build_actor(case_author_id)
    )


@pytest.mark.parametrize("open_count", [1, 3])
async def test_open_comments_are_counted_in_the_refusal(open_count: int) -> None:
    test_case = build_test_case(uuid7())

    with pytest.raises(ReviewCommentsOpenError) as refusal:
        await require_no_open_review_comments(CountingReviewCommentRepository(open_count), test_case)

    assert refusal.value.open_count == open_count


async def test_no_open_comment_passes() -> None:
    await require_no_open_review_comments(CountingReviewCommentRepository(0), build_test_case(uuid7()))
