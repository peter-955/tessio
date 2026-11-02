from datetime import UTC, datetime
from uuid import UUID

from app.modules.runs.domains.run_opening.entity import RunOpening
from app.modules.runs.domains.run_sheet.entity import RunSheet
from app.modules.runs.domains.suite_run_opening.entity import SuiteRunOpening
from app.modules.runs.errors import RunTargetRequiredError
from app.modules.runs.typing.enums import RunExecutor
from app.modules.runs.usecases.run_start_gate import RunStartGate
from app.modules.runs.utils.run_event import build_run_started_event, build_story_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccess, ProjectAccessResolver, require


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
        story_key: str | None,
        environment_id: UUID | None,
        test_case_ids: list[UUID] | None,
        suite_id: UUID | None = None,
    ) -> RunSheet:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.RUN_START)
            require(access, Capability.RUN_RECORD_MANUAL)
            if (story_key is None) == (suite_id is None):
                raise RunTargetRequiredError
            if suite_id is not None:
                sheet = await self._run_start_gate.open_suite_run(
                    access,
                    actor,
                    SuiteRunOpening(
                        suite_id=suite_id,
                        environment_id=environment_id,
                        executor=RunExecutor.MANUAL,
                        parent_run_id=None,
                        test_case_ids=test_case_ids,
                    ),
                    now,
                )
            else:
                sheet = await self._open_story_run(access, actor, story_key or "", environment_id, test_case_ids, now)
        await self._announce(sheet)
        return sheet

    async def _open_story_run(
        self,
        access: ProjectAccess,
        actor: Actor,
        story_key: str,
        environment_id: UUID | None,
        test_case_ids: list[UUID] | None,
        now: datetime,
    ) -> RunSheet:
        story_id = await self._run_start_gate.require_story_id(access.project_id, story_key)
        return await self._run_start_gate.open_run(
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

    async def _announce(self, sheet: RunSheet) -> None:
        await self._live_event_publisher.publish(build_run_started_event(sheet.run))
        if sheet.story_jira_key is not None:
            await self._live_event_publisher.publish(build_story_changed_event(sheet.run, sheet.story_jira_key))
