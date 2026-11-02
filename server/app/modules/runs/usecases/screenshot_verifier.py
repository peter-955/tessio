from collections import defaultdict
from pathlib import PurePosixPath
from uuid import UUID

from app.modules.files import StoredFile, StoredFileRepository, StoredFileStatus, build_screenshot_key_prefix
from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.domains.case_result.repository import CaseResultRepository
from app.modules.runs.domains.missing_screenshot.entity import MissingScreenshot
from app.modules.runs.domains.run_case_view.entity import RunCaseView
from app.modules.runs.domains.step_result.entity import StepResult
from app.modules.runs.typing.constants.screenshot import SCREENSHOT_CONTENT_TYPE_BY_SUFFIX
from app.shared.storage import ObjectStorage


class ScreenshotVerifier:
    def __init__(
        self,
        case_result_repository: CaseResultRepository,
        stored_file_repository: StoredFileRepository,
        object_storage: ObjectStorage,
    ) -> None:
        self._case_result_repository = case_result_repository
        self._stored_file_repository = stored_file_repository
        self._object_storage = object_storage

    async def verify(self, project_id: UUID, run_id: UUID, run_cases: list[RunCaseView]) -> list[MissingScreenshot]:
        codes_by_case_id = {run_case.test_case_id: run_case.code for run_case in run_cases}
        data_driven_case_ids = {run_case.test_case_id for run_case in run_cases if run_case.version.data_rows}
        case_results = await self._case_result_repository.list_for_run(run_id)
        steps_by_case_result_id: defaultdict[UUID, list[StepResult]] = defaultdict(list)
        for step_result in await self._case_result_repository.list_steps_for_run(run_id):
            if step_result.screenshot_file_id is not None:
                steps_by_case_result_id[step_result.case_result_id].append(step_result)
        missing_screenshots: list[MissingScreenshot] = []
        missing_file_ids: list[UUID] = []
        for case_result in case_results:
            unverified_steps = await self._list_unverified_steps(steps_by_case_result_id[case_result.id])
            if not unverified_steps:
                continue
            uploaded_keys = await self._list_uploaded_keys(project_id, case_result.id)
            for step_result, stored_file in unverified_steps:
                uploaded_key = uploaded_keys.get(str(step_result.step_order))
                if uploaded_key is not None:
                    await self._mark_uploaded(stored_file, uploaded_key)
                    continue
                missing_file_ids.append(stored_file.id)
                is_data_driven = case_result.test_case_id in data_driven_case_ids
                missing_screenshots.append(
                    self._build_missing(case_result, codes_by_case_id, step_result, is_data_driven)
                )
        await self._stored_file_repository.mark_missing(missing_file_ids)
        return missing_screenshots

    async def _list_unverified_steps(self, step_results: list[StepResult]) -> list[tuple[StepResult, StoredFile]]:
        unverified_steps: list[tuple[StepResult, StoredFile]] = []
        for step_result in step_results:
            if step_result.screenshot_file_id is None:
                continue
            stored_file = await self._stored_file_repository.find_by_id(step_result.screenshot_file_id)
            if stored_file is not None and not stored_file.is_uploaded:
                unverified_steps.append((step_result, stored_file))
        return unverified_steps

    async def _list_uploaded_keys(self, project_id: UUID, case_result_id: UUID) -> dict[str, str]:
        uploaded_keys: dict[str, str] = {}
        for key in await self._object_storage.list_keys(build_screenshot_key_prefix(project_id, case_result_id)):
            key_path = PurePosixPath(key)
            if key_path.suffix.lower() in SCREENSHOT_CONTENT_TYPE_BY_SUFFIX:
                uploaded_keys.setdefault(key_path.stem, key)
        return uploaded_keys

    async def _mark_uploaded(self, stored_file: StoredFile, key: str) -> None:
        key_path = PurePosixPath(key)
        head = await self._object_storage.head_object(key)
        await self._stored_file_repository.save(
            stored_file.model_copy(
                update={
                    "object_key": key,
                    "file_name": key_path.name,
                    "content_type": SCREENSHOT_CONTENT_TYPE_BY_SUFFIX[key_path.suffix.lower()],
                    "size": None if head is None else head.size,
                    "status": StoredFileStatus.UPLOADED,
                }
            )
        )

    @staticmethod
    def _build_missing(
        case_result: CaseResult, codes_by_case_id: dict[UUID, str], step_result: StepResult, is_data_driven: bool
    ) -> MissingScreenshot:
        return MissingScreenshot(
            case_result_id=case_result.id,
            test_case_id=case_result.test_case_id,
            code=codes_by_case_id.get(case_result.test_case_id, ""),
            step_order=step_result.step_order,
            iteration=case_result.iteration if is_data_driven else None,
        )
