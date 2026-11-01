from fastapi import Request

from app.modules.test_cases.usecases.attach_test_file import AttachTestFileUseCase
from app.modules.test_cases.usecases.change_test_case_status import ChangeTestCaseStatusUseCase
from app.modules.test_cases.usecases.commit_test_case_import import CommitTestCaseImportUseCase
from app.modules.test_cases.usecases.create_test_case import CreateTestCaseUseCase
from app.modules.test_cases.usecases.get_test_case import GetTestCaseUseCase
from app.modules.test_cases.usecases.list_test_case_versions import ListTestCaseVersionsUseCase
from app.modules.test_cases.usecases.list_test_cases import ListTestCasesUseCase
from app.modules.test_cases.usecases.list_test_file_versions import ListTestFileVersionsUseCase
from app.modules.test_cases.usecases.mark_test_case_reviewed import MarkTestCaseReviewedUseCase
from app.modules.test_cases.usecases.preview_test_case_import import PreviewTestCaseImportUseCase
from app.modules.test_cases.usecases.update_test_case import UpdateTestCaseUseCase


def get_list_test_cases(request: Request) -> ListTestCasesUseCase:
    use_case: ListTestCasesUseCase = request.app.state.container.list_test_cases
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
