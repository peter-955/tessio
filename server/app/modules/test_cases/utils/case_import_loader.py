from uuid import UUID

from app.modules.test_cases.domains.parsed_case_import.entity import ParsedCaseImport
from app.modules.test_cases.errors import (
    CaseImportFileNotFoundError,
    CaseImportFileTooLargeError,
    CaseImportUploadNotCompletedError,
)
from app.modules.test_cases.typing.constants import MAX_CASE_IMPORT_BYTES
from app.modules.test_cases.utils.case_import_parser import parse_case_import
from app.modules.test_data import ImportFileReader


async def load_case_import(
    import_file_reader: ImportFileReader, project_id: UUID, file_id: UUID, uploaded_by: UUID
) -> ParsedCaseImport:
    import_file = await import_file_reader.find(project_id, file_id, uploaded_by)
    if import_file is None:
        raise CaseImportFileNotFoundError
    if not import_file.is_uploaded:
        raise CaseImportUploadNotCompletedError
    if import_file.size is not None and import_file.size > MAX_CASE_IMPORT_BYTES:
        raise CaseImportFileTooLargeError
    content = await import_file_reader.read_content(import_file)
    if content is None:
        raise CaseImportFileNotFoundError
    if len(content) > MAX_CASE_IMPORT_BYTES:
        raise CaseImportFileTooLargeError
    return parse_case_import(import_file.file_name, content)
