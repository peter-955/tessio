from uuid import UUID

from app.modules.test_data.domains.parsed_import.entity import ParsedImport
from app.modules.test_data.errors import ImportFileNotFoundError, ImportFileTooLargeError, ImportUploadNotCompletedError
from app.modules.test_data.ports.import_file_reader import ImportFileReader
from app.modules.test_data.typing.constants import MAX_IMPORT_BYTES
from app.modules.test_data.utils.import_file_parser import parse_import_file


async def load_parsed_import(
    import_file_reader: ImportFileReader, project_id: UUID, file_id: UUID, uploaded_by: UUID
) -> ParsedImport:
    import_file = await import_file_reader.find(project_id, file_id, uploaded_by)
    if import_file is None:
        raise ImportFileNotFoundError
    if not import_file.is_uploaded:
        raise ImportUploadNotCompletedError
    if import_file.size is not None and import_file.size > MAX_IMPORT_BYTES:
        raise ImportFileTooLargeError
    content = await import_file_reader.read_content(import_file)
    if content is None:
        raise ImportFileNotFoundError
    if len(content) > MAX_IMPORT_BYTES:
        raise ImportFileTooLargeError
    return parse_import_file(import_file.file_name, content)
