from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.modules.files.dependencies import (
    get_complete_upload,
    get_create_avatar_upload,
    get_create_download_link,
    get_create_upload,
)
from app.modules.files.models.create_avatar_upload_request import CreateAvatarUploadRequest
from app.modules.files.models.create_upload_request import CreateUploadRequest
from app.modules.files.models.download_link_response import DownloadLinkResponse
from app.modules.files.models.signed_upload_response import SignedUploadResponse
from app.modules.files.models.stored_file_response import StoredFileResponse
from app.modules.files.usecases.complete_upload import CompleteUploadUseCase
from app.modules.files.usecases.create_avatar_upload import CreateAvatarUploadUseCase
from app.modules.files.usecases.create_download_link import CreateDownloadLinkUseCase
from app.modules.files.usecases.create_upload import CreateUploadUseCase
from app.modules.files.utils.file_responses import build_signed_upload_response, build_stored_file_response
from app.modules.projects import get_signed_in_actor
from app.shared.permissions import Actor

files_router = APIRouter(prefix="/api", tags=["files"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]


@files_router.post("/projects/{project_key}/uploads", status_code=status.HTTP_201_CREATED)
async def create_upload(
    project_key: str,
    body: CreateUploadRequest,
    actor: SignedInActor,
    use_case: Annotated[CreateUploadUseCase, Depends(get_create_upload)],
) -> SignedUploadResponse:
    created_upload = await use_case.execute(actor, project_key, body.kind, body.file_name, body.content_type, body.size)
    return build_signed_upload_response(created_upload)


@files_router.post("/projects/{project_key}/uploads/{file_id}/complete")
async def complete_upload(
    project_key: str,
    file_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[CompleteUploadUseCase, Depends(get_complete_upload)],
) -> StoredFileResponse:
    return build_stored_file_response(await use_case.execute(actor, file_id, project_key))


@files_router.get("/projects/{project_key}/files/{file_id}")
async def create_download_link(
    project_key: str,
    file_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[CreateDownloadLinkUseCase, Depends(get_create_download_link)],
) -> DownloadLinkResponse:
    download_link = await use_case.execute(actor, project_key, file_id)
    return DownloadLinkResponse(url=download_link.url, expires_at=download_link.expires_at)


@files_router.post("/me/avatar-upload", status_code=status.HTTP_201_CREATED)
async def create_avatar_upload(
    body: CreateAvatarUploadRequest,
    actor: SignedInActor,
    use_case: Annotated[CreateAvatarUploadUseCase, Depends(get_create_avatar_upload)],
) -> SignedUploadResponse:
    created_upload = await use_case.execute(actor, body.file_name, body.content_type, body.size)
    return build_signed_upload_response(created_upload)


@files_router.post("/me/avatar-upload/{file_id}/complete")
async def complete_avatar_upload(
    file_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[CompleteUploadUseCase, Depends(get_complete_upload)],
) -> StoredFileResponse:
    return build_stored_file_response(await use_case.execute(actor, file_id, None))
