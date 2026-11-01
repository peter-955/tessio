from app.modules.files.domains.created_upload.entity import CreatedUpload
from app.modules.files.domains.stored_file.entity import StoredFile
from app.modules.files.typing.constants.signed_upload import CONTENT_TYPE_FIELD
from app.shared.storage import SignedObjectUpload


def build_created_upload(stored_file: StoredFile, signed_upload: SignedObjectUpload) -> CreatedUpload:
    return CreatedUpload(
        file_id=stored_file.id,
        url=signed_upload.url,
        fields={**signed_upload.fields, CONTENT_TYPE_FIELD: stored_file.content_type},
        object_key=stored_file.object_key,
    )
