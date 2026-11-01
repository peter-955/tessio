from datetime import UTC, datetime

from pydantic import JsonValue

from app.modules.files.usecases.delete_orphan_files import DeleteOrphanFilesUseCase
from app.shared.queue import JobHandler


class DeleteOrphanFilesJobHandler(JobHandler):
    def __init__(self, use_case: DeleteOrphanFilesUseCase) -> None:
        self._use_case = use_case

    async def handle(self, data: dict[str, JsonValue]) -> None:
        await self._use_case.execute(datetime.now(UTC))
