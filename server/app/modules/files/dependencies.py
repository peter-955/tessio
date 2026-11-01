from fastapi import Request

from app.modules.files.usecases.complete_upload import CompleteUploadUseCase
from app.modules.files.usecases.create_avatar_upload import CreateAvatarUploadUseCase
from app.modules.files.usecases.create_download_link import CreateDownloadLinkUseCase
from app.modules.files.usecases.create_upload import CreateUploadUseCase


def get_create_upload(request: Request) -> CreateUploadUseCase:
    use_case: CreateUploadUseCase = request.app.state.container.create_upload
    return use_case


def get_complete_upload(request: Request) -> CompleteUploadUseCase:
    use_case: CompleteUploadUseCase = request.app.state.container.complete_upload
    return use_case


def get_create_download_link(request: Request) -> CreateDownloadLinkUseCase:
    use_case: CreateDownloadLinkUseCase = request.app.state.container.create_download_link
    return use_case


def get_create_avatar_upload(request: Request) -> CreateAvatarUploadUseCase:
    use_case: CreateAvatarUploadUseCase = request.app.state.container.create_avatar_upload
    return use_case
