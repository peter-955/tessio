from datetime import UTC, datetime

from pydantic import JsonValue

from app.modules.auth.usecases.delete_expired_sessions import DeleteExpiredSessionsUseCase
from app.shared.logging import get_logger
from app.shared.queue import JobHandler

log = get_logger(__name__)


class DeleteExpiredSessionsJobHandler(JobHandler):
    def __init__(self, use_case: DeleteExpiredSessionsUseCase) -> None:
        self._use_case = use_case

    async def handle(self, data: dict[str, JsonValue]) -> None:
        deleted_count = await self._use_case.execute(datetime.now(UTC))
        log.info("sessions.expired_deleted", extra={"count": deleted_count})
