from fastapi import Request

from app.modules.run_logs.usecases.get_run_log import GetRunLogUseCase
from app.modules.run_logs.usecases.upload_run_log import UploadRunLogUseCase


def get_upload_run_log(request: Request) -> UploadRunLogUseCase:
    use_case: UploadRunLogUseCase = request.app.state.container.upload_run_log
    return use_case


def get_get_run_log(request: Request) -> GetRunLogUseCase:
    use_case: GetRunLogUseCase = request.app.state.container.get_run_log
    return use_case
