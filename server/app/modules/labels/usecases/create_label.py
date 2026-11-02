from datetime import UTC, datetime
from uuid import uuid7

from app.modules.labels.domains.label.entity import Label
from app.modules.labels.domains.label.repository import LabelRepository
from app.modules.labels.domains.label_summary.entity import LabelSummary
from app.modules.labels.errors import LabelNameAlreadyUsedError
from app.modules.labels.typing.enums import LabelColor
from app.modules.labels.utils.label_event import build_label_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class CreateLabelUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        label_repository: LabelRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._label_repository = label_repository
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, name: str, color: LabelColor) -> LabelSummary:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_EDIT)
            if await self._label_repository.find_by_name(access.project_id, name) is not None:
                raise LabelNameAlreadyUsedError
            label = Label(
                id=uuid7(),
                project_id=access.project_id,
                name=name,
                color=color,
                created_by=actor.user_id,
                created_at=datetime.now(UTC),
            )
            await self._label_repository.save(label)
        await self._live_event_publisher.publish(build_label_changed_event(label))
        return LabelSummary(label=label, case_count=0)
