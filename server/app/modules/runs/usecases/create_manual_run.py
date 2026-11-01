from datetime import UTC, datetime
from uuid import UUID

from app.modules.runs.domains.run_opening.entity import RunOpening
from app.modules.runs.domains.run_sheet.entity import RunSheet
from app.modules.runs.typing.enums import RunExecutor
from app.modules.runs.usecases.run_start_gate import RunStartGate
from app.shared.common import Transaction
from app.shared.events import LiveEvent, LiveEventPublisher, LiveEventType
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class CreateManualRunUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        run_start_gate: RunStartGate,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._run_start_gate = run_start_gate
        self._live_event_publisher = live_event_publisher

    async def execute(
        self,
        actor: Actor,
        project_key: str,
        story_key: str,
        environment_id: UUID | None,
        test_case_ids: list[UUID] | None,
    ) -> RunSheet:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.RUN_START)
            require(access, Capability.RUN_RECORD_MANUAL)
            story_id = await self._run_start_gate.require_story_id(access.project_id, story_key)
            sheet = await self._run_start_gate.open_run(
                access,
                actor,
                RunOpening(
                    story_id=story_id,
                    environment_id=environment_id,
                    executor=RunExecutor.MANUAL,
                    parent_run_id=None,
                    test_case_ids=test_case_ids,
                ),
                now,
            )
        await self._announce(sheet)
        return sheet

    async def _announce(self, sheet: RunSheet) -> None:
        run = sheet.run
        await self._live_event_publisher.publish(
            LiveEvent(
                type=LiveEventType.RUN_STARTED,
                project_id=run.project_id,
                ids={"runId": str(run.id), "storyId": str(run.story_id)},
            )
        )
        await self._live_event_publisher.publish(
            LiveEvent(
                type=LiveEventType.STORY_CHANGED,
                project_id=run.project_id,
                ids={"storyId": str(run.story_id), "jiraKey": sheet.story_jira_key},
            )
        )
