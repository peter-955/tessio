from datetime import UTC, datetime
from uuid import UUID

from app.modules.shared_steps.domains.shared_step.entity import SharedStep
from app.modules.shared_steps.domains.shared_step.repository import SharedStepRepository
from app.modules.shared_steps.domains.shared_step_changes.entity import SharedStepChanges
from app.modules.shared_steps.domains.shared_step_detail.entity import SharedStepDetail
from app.modules.shared_steps.domains.shared_step_version.entity import SharedStepVersion
from app.modules.shared_steps.errors import SharedStepMakesCaseTooLongError, SharedStepVersionConflictError
from app.modules.shared_steps.ports.shared_step_usage_reader import SharedStepUsageReader
from app.modules.shared_steps.typing.constants import MAX_EXPANDED_CASE_STEPS
from app.modules.shared_steps.utils.expanded_step_count import count_expanded_steps
from app.modules.shared_steps.utils.shared_step_event import build_shared_step_changed_event
from app.modules.shared_steps.utils.shared_step_lookup import (
    require_current_shared_step_version,
    require_locked_shared_step,
)
from app.modules.shared_steps.utils.shared_step_version import build_shared_step_version
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class UpdateSharedStepUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        shared_step_repository: SharedStepRepository,
        shared_step_usage_reader: SharedStepUsageReader,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._shared_step_repository = shared_step_repository
        self._shared_step_usage_reader = shared_step_usage_reader
        self._live_event_publisher = live_event_publisher

    async def execute(
        self, actor: Actor, project_key: str, key: str, base_version_number: int, changes: SharedStepChanges
    ) -> SharedStepDetail:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_EDIT)
            shared_step = await require_locked_shared_step(self._shared_step_repository, access.project_id, key)
            current_version = await require_current_shared_step_version(self._shared_step_repository, shared_step)
            if base_version_number != current_version.number:
                raise SharedStepVersionConflictError
            updated_step = self._apply_header_changes(shared_step, changes, now)
            version = current_version
            if changes.steps is not None and self._is_changing_steps(current_version, changes):
                await self._require_case_step_limit(access.project_id, shared_step.key, len(changes.steps))
                version = build_shared_step_version(
                    shared_step.id, current_version.number + 1, changes.steps, actor.user_id, now
                )
                updated_step = updated_step.model_copy(update={"current_version_id": version.id})
                await self._shared_step_repository.add_version(updated_step, version)
            elif updated_step != shared_step:
                await self._shared_step_repository.save(updated_step)
            usage_counts = await self._shared_step_usage_reader.count_cases(access.project_id, [shared_step.key])
        if updated_step != shared_step:
            await self._live_event_publisher.publish(build_shared_step_changed_event(updated_step))
        return SharedStepDetail(
            shared_step=updated_step, version=version, usage_count=usage_counts.get(shared_step.key, 0)
        )

    async def _require_case_step_limit(self, project_id: UUID, key: str, action_count: int) -> None:
        cases = await self._shared_step_usage_reader.list_case_step_keys(project_id, key)
        other_keys = {step_key for case in cases for step_key in case.step_keys if step_key is not None} - {key}
        current_steps = await self._shared_step_repository.list_current_by_keys(project_id, other_keys)
        action_counts = {current.shared_step.key: len(current.version.steps) for current in current_steps}
        action_counts[key] = action_count
        too_long_codes = [
            case.code for case in cases if count_expanded_steps(case.step_keys, action_counts) > MAX_EXPANDED_CASE_STEPS
        ]
        if too_long_codes:
            raise SharedStepMakesCaseTooLongError(too_long_codes)

    @staticmethod
    def _apply_header_changes(shared_step: SharedStep, changes: SharedStepChanges, now: datetime) -> SharedStep:
        archived_at = shared_step.archived_at
        if changes.is_archived is True and archived_at is None:
            archived_at = now
        elif changes.is_archived is False:
            archived_at = None
        return shared_step.model_copy(
            update={
                "title": shared_step.title if changes.title is None else changes.title,
                "archived_at": archived_at,
            }
        )

    @staticmethod
    def _is_changing_steps(current_version: SharedStepVersion, changes: SharedStepChanges) -> bool:
        current_steps = [(step.action, step.expected) for step in current_version.steps]
        new_steps = [(step.action, step.expected) for step in changes.steps or []]
        return current_steps != new_steps
