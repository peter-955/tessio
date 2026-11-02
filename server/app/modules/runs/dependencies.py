from fastapi import Request

from app.modules.runs.usecases.create_manual_run import CreateManualRunUseCase
from app.modules.runs.usecases.create_screenshot_upload import CreateScreenshotUploadUseCase
from app.modules.runs.usecases.finish_manual_run import FinishManualRunUseCase
from app.modules.runs.usecases.get_run import GetRunUseCase
from app.modules.runs.usecases.import_junit_run import ImportJunitRunUseCase
from app.modules.runs.usecases.list_runs import ListRunsUseCase
from app.modules.runs.usecases.record_manual_case_result import RecordManualCaseResultUseCase
from app.modules.runs.usecases.rerun_failed_cases import RerunFailedCasesUseCase


def get_create_screenshot_upload(request: Request) -> CreateScreenshotUploadUseCase:
    use_case: CreateScreenshotUploadUseCase = request.app.state.container.create_screenshot_upload
    return use_case


def get_list_runs(request: Request) -> ListRunsUseCase:
    use_case: ListRunsUseCase = request.app.state.container.list_runs
    return use_case


def get_get_run(request: Request) -> GetRunUseCase:
    use_case: GetRunUseCase = request.app.state.container.get_run
    return use_case


def get_create_manual_run(request: Request) -> CreateManualRunUseCase:
    use_case: CreateManualRunUseCase = request.app.state.container.create_manual_run
    return use_case


def get_record_manual_case_result(request: Request) -> RecordManualCaseResultUseCase:
    use_case: RecordManualCaseResultUseCase = request.app.state.container.record_manual_case_result
    return use_case


def get_finish_manual_run(request: Request) -> FinishManualRunUseCase:
    use_case: FinishManualRunUseCase = request.app.state.container.finish_manual_run
    return use_case


def get_rerun_failed_cases(request: Request) -> RerunFailedCasesUseCase:
    use_case: RerunFailedCasesUseCase = request.app.state.container.rerun_failed_cases
    return use_case


def get_import_junit_run(request: Request) -> ImportJunitRunUseCase:
    use_case: ImportJunitRunUseCase = request.app.state.container.import_junit_run
    return use_case
