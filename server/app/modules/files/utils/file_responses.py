from app.modules.files.domains.created_upload.entity import CreatedUpload
from app.modules.files.domains.stored_file.entity import StoredFile
from app.modules.files.models.signed_upload_response import SignedUploadResponse
from app.modules.files.models.stored_file_response import StoredFileResponse


def build_signed_upload_response(created_upload: CreatedUpload) -> SignedUploadResponse:
    return SignedUploadResponse(
        file_id=created_upload.file_id,
        url=created_upload.url,
        fields=created_upload.fields,
        object_key=created_upload.object_key,
    )


def build_stored_file_response(stored_file: StoredFile) -> StoredFileResponse:
    return StoredFileResponse(
        id=stored_file.id,
        kind=stored_file.kind,
        file_name=stored_file.file_name,
        content_type=stored_file.content_type,
        size=stored_file.size,
        status=stored_file.status,
        created_at=stored_file.created_at,
    )
