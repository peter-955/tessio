from sqlalchemy import Text, Uuid, column, table

STORED_FILE_VIEW = table(
    "stored_files",
    column("id", Uuid()),
    column("kind", Text()),
    column("status", Text()),
    column("uploaded_by", Uuid()),
    column("object_key", Text()),
    column("file_name", Text()),
)
