from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.files import StoredFileKind, StoredFileRepository
from app.modules.labels import TestCaseLabelRepository
from app.modules.test_cases.domains.test_case.entity import TestCase
from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.domains.test_case_detail.entity import TestCaseDetail
from app.modules.test_cases.domains.test_case_version.repository import TestCaseVersionRepository
from app.modules.test_cases.domains.test_file.entity import TestFile
from app.modules.test_cases.domains.test_file.repository import TestFileRepository
from app.modules.test_cases.domains.test_file_version.entity import TestFileVersion
from app.modules.test_cases.domains.test_file_version.repository import TestFileVersionRepository
from app.modules.test_cases.errors import (
    StoredFileAlreadyAttachedError,
    StoredFileNotUsableError,
    TestCaseDeprecatedError,
    TestCaseVersionConflictError,
    TestFileNotFoundError,
    UploadNotCompletedError,
)
from app.modules.test_cases.ports.criterion_reader import CriterionReader
from app.modules.test_cases.ports.data_key_reader import DataKeyReader
from app.modules.test_cases.ports.story_reader import StoryReader
from app.modules.test_cases.typing.constants.flaky_case import FLAKY_STATE_RESET
from app.modules.test_cases.utils.test_case_changes import build_version_content
from app.modules.test_cases.utils.test_case_detail import load_test_case_detail
from app.modules.test_cases.utils.test_case_event import build_test_case_changed_event
from app.modules.test_cases.utils.test_case_lookup import require_current_version, require_locked_test_case
from app.modules.test_cases.utils.test_case_version import build_test_case_version
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class AttachTestFileUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_case_repository: TestCaseRepository,
        test_case_version_repository: TestCaseVersionRepository,
        test_file_repository: TestFileRepository,
        story_reader: StoryReader,
        criterion_reader: CriterionReader,
        data_key_reader: DataKeyReader,
        test_case_label_repository: TestCaseLabelRepository,
        test_file_version_repository: TestFileVersionRepository,
        stored_file_repository: StoredFileRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_case_repository = test_case_repository
        self._test_case_version_repository = test_case_version_repository
        self._test_file_repository = test_file_repository
        self._story_reader = story_reader
        self._criterion_reader = criterion_reader
        self._data_key_reader = data_key_reader
        self._test_case_label_repository = test_case_label_repository
        self._test_file_version_repository = test_file_version_repository
        self._stored_file_repository = stored_file_repository
        self._live_event_publisher = live_event_publisher

    async def execute(
        self,
        actor: Actor,
        project_key: str,
        case_code: str,
        key: str,
        stored_file_id: UUID,
        base_version_number: int,
    ) -> TestCaseDetail:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_EDIT)
            test_case = await require_locked_test_case(self._test_case_repository, access.project_id, case_code)
            if test_case.is_deprecated:
                raise TestCaseDeprecatedError
            current_version = await require_current_version(self._test_case_version_repository, test_case)
            if base_version_number != current_version.number:
                raise TestCaseVersionConflictError
            await self._require_attachable(access.project_id, stored_file_id)
            await self._store_file_version(test_case, key, stored_file_id, actor.user_id, now)
            files = await self._test_file_repository.list_for_case(test_case.id)
            version = build_test_case_version(
                test_case.id,
                current_version.number + 1,
                build_version_content(current_version),
                [file.current_version.version.id for file in sorted(files, key=lambda file: file.test_file.key)],
                actor.user_id,
                now,
                current_version.data_keys,
            )
            test_case = test_case.model_copy(update={"current_version_id": version.id, **FLAKY_STATE_RESET})
            await self._test_case_repository.add_version(test_case, version)
            detail = await load_test_case_detail(
                test_case,
                self._test_case_version_repository,
                self._test_file_repository,
                self._story_reader,
                self._criterion_reader,
                self._data_key_reader,
                self._test_case_label_repository,
            )
        await self._live_event_publisher.publish(build_test_case_changed_event(test_case))
        return detail

    async def _require_attachable(self, project_id: UUID, stored_file_id: UUID) -> None:
        stored_file = await self._stored_file_repository.find_by_id(stored_file_id)
        if stored_file is None or stored_file.project_id != project_id:
            raise TestFileNotFoundError
        if stored_file.kind is not StoredFileKind.TEST_FILE:
            raise StoredFileNotUsableError
        if not stored_file.is_uploaded:
            raise UploadNotCompletedError
        if await self._test_file_version_repository.exists_for_stored_file(stored_file_id):
            raise StoredFileAlreadyAttachedError

    async def _store_file_version(
        self, test_case: TestCase, key: str, stored_file_id: UUID, created_by: UUID, now: datetime
    ) -> None:
        test_file = await self._test_file_repository.find_by_key(test_case.id, key)
        if test_file is None:
            test_file_id = uuid7()
            version = self._build_file_version(test_file_id, 1, stored_file_id, created_by, now)
            await self._test_file_repository.create(
                TestFile(
                    id=test_file_id,
                    project_id=test_case.project_id,
                    test_case_id=test_case.id,
                    key=key,
                    current_version_id=version.id,
                    created_by=created_by,
                    created_at=now,
                ),
                version,
            )
            return
        versions = await self._test_file_version_repository.list_for_file(test_file.id)
        number = max((detail.version.number for detail in versions), default=0) + 1
        version = self._build_file_version(test_file.id, number, stored_file_id, created_by, now)
        await self._test_file_repository.add_version(
            test_file.model_copy(update={"current_version_id": version.id}), version
        )

    @staticmethod
    def _build_file_version(
        test_file_id: UUID, number: int, stored_file_id: UUID, created_by: UUID, now: datetime
    ) -> TestFileVersion:
        return TestFileVersion(
            id=uuid7(),
            test_file_id=test_file_id,
            number=number,
            stored_file_id=stored_file_id,
            created_by=created_by,
            created_at=now,
        )
