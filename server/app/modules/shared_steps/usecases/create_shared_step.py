import re
from datetime import UTC, datetime
from uuid import uuid7

from app.modules.shared_steps.domains.shared_step.entity import SharedStep
from app.modules.shared_steps.domains.shared_step.repository import SharedStepRepository
from app.modules.shared_steps.domains.shared_step_action.entity import SharedStepAction
from app.modules.shared_steps.domains.shared_step_detail.entity import SharedStepDetail
from app.modules.shared_steps.errors import InvalidSharedStepKeyError, SharedStepKeyAlreadyUsedError
from app.modules.shared_steps.typing.constants import SHARED_STEP_KEY_PATTERN
from app.modules.shared_steps.utils.shared_step_event import build_shared_step_changed_event
from app.modules.shared_steps.utils.shared_step_lookup import normalize_shared_step_key
from app.modules.shared_steps.utils.shared_step_version import build_shared_step_version
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class CreateSharedStepUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        shared_step_repository: SharedStepRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._shared_step_repository = shared_step_repository
        self._live_event_publisher = live_event_publisher

    async def execute(
        self, actor: Actor, project_key: str, key: str, title: str, actions: list[SharedStepAction]
    ) -> SharedStepDetail:
        now = datetime.now(UTC)
        normalized_key = normalize_shared_step_key(key)
        if re.fullmatch(SHARED_STEP_KEY_PATTERN, normalized_key) is None:
            raise InvalidSharedStepKeyError
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_EDIT)
            if await self._shared_step_repository.find_by_key(access.project_id, normalized_key) is not None:
                raise SharedStepKeyAlreadyUsedError
            shared_step_id = uuid7()
            version = build_shared_step_version(shared_step_id, 1, actions, actor.user_id, now)
            shared_step = SharedStep(
                id=shared_step_id,
                project_id=access.project_id,
                key=normalized_key,
                title=title,
                current_version_id=version.id,
                archived_at=None,
                created_by=actor.user_id,
                created_at=now,
            )
            await self._shared_step_repository.add(shared_step, version)
        await self._live_event_publisher.publish(build_shared_step_changed_event(shared_step))
        return SharedStepDetail(shared_step=shared_step, version=version, usage_count=0)
