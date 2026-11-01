from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.story_context.domains.run_file.entity import RunFile
from app.modules.story_context.domains.test_file_link.entity import TestFileLink
from app.modules.story_context.errors import TestFileKeyAmbiguousError, TestFileNotFoundError
from app.modules.story_context.ports.run_file_recorder import RunFileRecorder
from app.modules.story_context.ports.run_scope_reader import RunScopeReader
from app.modules.story_context.typing.constants import TEST_FILE_LINK_LIFETIME
from app.modules.story_context.utils.run_ownership import ensure_own_running_run
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require
from app.shared.storage import ObjectStorage


class GetTestFileUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        run_scope_reader: RunScopeReader,
        run_file_recorder: RunFileRecorder,
        object_storage: ObjectStorage,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._run_scope_reader = run_scope_reader
        self._run_file_recorder = run_file_recorder
        self._object_storage = object_storage

    async def execute_in_token_project(
        self, actor: Actor, run_id: UUID, key: str, case_id: UUID | None
    ) -> TestFileLink:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve_by_id(actor, actor.token_project_id)
            require(access, Capability.RUN_START)
            run = ensure_own_running_run(await self._run_scope_reader.find_run(access.project_id, run_id), actor)
            files = await self._run_scope_reader.list_test_files(run.id, key.strip(), case_id)
            if not files:
                raise TestFileNotFoundError
            if len({file.test_file_version_id for file in files}) > 1:
                raise TestFileKeyAmbiguousError
            test_file = files[0]
            if not test_file.is_uploaded:
                raise TestFileNotFoundError
            await self._run_file_recorder.record(
                RunFile(
                    id=uuid7(),
                    run_id=run.id,
                    test_case_id=test_file.test_case_id,
                    test_file_version_id=test_file.test_file_version_id,
                    key=test_file.key,
                    requested_by=actor.user_id,
                    created_at=datetime.now(UTC),
                )
            )
        url = self._object_storage.create_signed_download(
            test_file.object_key, TEST_FILE_LINK_LIFETIME, test_file.file_name
        )
        return TestFileLink(file_name=test_file.file_name, url=url)
