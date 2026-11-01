from uuid import UUID

from app.modules.test_cases.domains.case_references.entity import CaseReferences
from app.modules.test_cases.domains.test_file.repository import TestFileRepository
from app.modules.test_cases.ports.data_key_reader import DataKeyReader


async def load_available_references(
    data_key_reader: DataKeyReader, test_file_repository: TestFileRepository, project_id: UUID, test_case_id: UUID
) -> CaseReferences:
    files = await test_file_repository.list_for_case(test_case_id)
    return CaseReferences(
        data_keys=await data_key_reader.list_keys(project_id),
        file_keys=frozenset(file.test_file.key for file in files),
    )
