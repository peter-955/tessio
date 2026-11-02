from fastapi import Request

from app.modules.test_cases.usecases.add_review_comment import AddReviewCommentUseCase
from app.modules.test_cases.usecases.attach_test_file import AttachTestFileUseCase
from app.modules.test_cases.usecases.change_test_case_status import ChangeTestCaseStatusUseCase
from app.modules.test_cases.usecases.commit_test_case_import import CommitTestCaseImportUseCase
from app.modules.test_cases.usecases.create_test_case import CreateTestCaseUseCase
from app.modules.test_cases.usecases.get_test_case import GetTestCaseUseCase
from app.modules.test_cases.usecases.list_quarantine_events import ListQuarantineEventsUseCase
from app.modules.test_cases.usecases.list_review_comments import ListReviewCommentsUseCase
from app.modules.test_cases.usecases.list_test_case_versions import ListTestCaseVersionsUseCase
from app.modules.test_cases.usecases.list_test_cases import ListTestCasesUseCase
from app.modules.test_cases.usecases.list_test_file_versions import ListTestFileVersionsUseCase
from app.modules.test_cases.usecases.mark_test_case_reviewed import MarkTestCaseReviewedUseCase
from app.modules.test_cases.usecases.preview_test_case_import import PreviewTestCaseImportUseCase
from app.modules.test_cases.usecases.quarantine_test_case import QuarantineTestCaseUseCase
from app.modules.test_cases.usecases.release_test_case_quarantine import ReleaseTestCaseQuarantineUseCase
from app.modules.test_cases.usecases.resolve_review_comment import ResolveReviewCommentUseCase
from app.modules.test_cases.usecases.set_test_case_labels import SetTestCaseLabelsUseCase
from app.modules.test_cases.usecases.update_test_case import UpdateTestCaseUseCase


def get_list_test_cases(request: Request) -> ListTestCasesUseCase:
    use_case: ListTestCasesUseCase = request.app.state.container.list_test_cases
    return use_case


def get_quarantine_test_case(request: Request) -> QuarantineTestCaseUseCase:
    use_case: QuarantineTestCaseUseCase = request.app.state.container.quarantine_test_case
    return use_case


def get_release_test_case_quarantine(request: Request) -> ReleaseTestCaseQuarantineUseCase:
    use_case: ReleaseTestCaseQuarantineUseCase = request.app.state.container.release_test_case_quarantine
    return use_case


def get_list_quarantine_events(request: Request) -> ListQuarantineEventsUseCase:
    use_case: ListQuarantineEventsUseCase = request.app.state.container.list_quarantine_events
    return use_case


def get_get_test_case(request: Request) -> GetTestCaseUseCase:
    use_case: GetTestCaseUseCase = request.app.state.container.get_test_case
    return use_case


def get_create_test_case(request: Request) -> CreateTestCaseUseCase:
    use_case: CreateTestCaseUseCase = request.app.state.container.create_test_case
    return use_case


def get_update_test_case(request: Request) -> UpdateTestCaseUseCase:
    use_case: UpdateTestCaseUseCase = request.app.state.container.update_test_case
    return use_case


def get_list_test_case_versions(request: Request) -> ListTestCaseVersionsUseCase:
    use_case: ListTestCaseVersionsUseCase = request.app.state.container.list_test_case_versions
    return use_case


def get_change_test_case_status(request: Request) -> ChangeTestCaseStatusUseCase:
    use_case: ChangeTestCaseStatusUseCase = request.app.state.container.change_test_case_status
    return use_case


def get_mark_test_case_reviewed(request: Request) -> MarkTestCaseReviewedUseCase:
    use_case: MarkTestCaseReviewedUseCase = request.app.state.container.mark_test_case_reviewed
    return use_case


def get_attach_test_file(request: Request) -> AttachTestFileUseCase:
    use_case: AttachTestFileUseCase = request.app.state.container.attach_test_file
    return use_case


def get_list_test_file_versions(request: Request) -> ListTestFileVersionsUseCase:
    use_case: ListTestFileVersionsUseCase = request.app.state.container.list_test_file_versions
    return use_case


def get_preview_test_case_import(request: Request) -> PreviewTestCaseImportUseCase:
    use_case: PreviewTestCaseImportUseCase = request.app.state.container.preview_test_case_import
    return use_case


def get_commit_test_case_import(request: Request) -> CommitTestCaseImportUseCase:
    use_case: CommitTestCaseImportUseCase = request.app.state.container.commit_test_case_import
    return use_case


def get_set_test_case_labels(request: Request) -> SetTestCaseLabelsUseCase:
    use_case: SetTestCaseLabelsUseCase = request.app.state.container.set_test_case_labels
    return use_case


def get_list_review_comments(request: Request) -> ListReviewCommentsUseCase:
    use_case: ListReviewCommentsUseCase = request.app.state.container.list_review_comments
    return use_case


def get_add_review_comment(request: Request) -> AddReviewCommentUseCase:
    use_case: AddReviewCommentUseCase = request.app.state.container.add_review_comment
    return use_case


def get_resolve_review_comment(request: Request) -> ResolveReviewCommentUseCase:
    use_case: ResolveReviewCommentUseCase = request.app.state.container.resolve_review_comment
    return use_case
