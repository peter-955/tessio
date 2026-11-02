from uuid import UUID

from app.modules.labels.domains.label.repository import LabelRepository
from app.modules.labels.errors import LabelNotFoundError
from app.modules.labels.utils.label_event import build_label_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class DeleteLabelUseCase:
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

    async def execute(self, actor: Actor, project_key: str, label_id: UUID) -> None:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_EDIT)
            label = await self._label_repository.find_by_id(access.project_id, label_id)
            if label is None:
                raise LabelNotFoundError
            await self._label_repository.delete(label.id)
        await self._live_event_publisher.publish(build_label_changed_event(label))
