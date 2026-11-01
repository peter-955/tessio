from uuid import UUID

from app.modules.files import build_screenshot_key_prefix
from app.modules.runs.domains.case_result.repository import CaseResultRepository
from app.modules.runs.domains.run.repository import RunRepository
from app.modules.runs.errors import CaseResultNotFoundError, RunNotFoundError, RunNotOwnedError
from app.modules.runs.typing.constants.screenshot import (
    MAX_SCREENSHOT_BYTES,
    SCREENSHOT_CONTENT_TYPE_PREFIX,
    SCREENSHOT_UPLOAD_LIFETIME,
)
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require
from app.shared.storage import ObjectStorage, SignedUpload


class CreateScreenshotUploadUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        run_repository: RunRepository,
        case_result_repository: CaseResultRepository,
        object_storage: ObjectStorage,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._run_repository = run_repository
        self._case_result_repository = case_result_repository
        self._object_storage = object_storage

    async def execute(self, actor: Actor, run_id: UUID, case_result_id: UUID) -> SignedUpload:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve_by_id(actor, actor.token_project_id)
            require(access, Capability.RUN_START)
            run = await self._run_repository.find_by_id(access.project_id, run_id)
            if run is None:
                raise RunNotFoundError
            if run.started_by != actor.user_id:
                raise RunNotOwnedError
            case_result = await self._case_result_repository.find_by_id(run.id, case_result_id)
            if case_result is None:
                raise CaseResultNotFoundError
        return self._object_storage.create_signed_upload(
            build_screenshot_key_prefix(run.project_id, case_result.id),
            MAX_SCREENSHOT_BYTES,
            SCREENSHOT_UPLOAD_LIFETIME,
            SCREENSHOT_CONTENT_TYPE_PREFIX,
        )
