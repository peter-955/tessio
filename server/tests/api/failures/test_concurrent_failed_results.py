import asyncio

from httpx import AsyncClient

from app.container import Container
from app.modules.failures import ApplyCaseResultUseCase, FailureEventKind
from app.modules.runs import ResultStatus
from tests.api.failures.failure_steps import (
    list_event_rows,
    list_failure_rows,
    seed_case_result,
    seed_run,
    seed_scenario,
)
from tests.api.failures.slow_failure_repository import SlowFailureRepository
from tests.conftest import RecordingMailer


async def test_concurrent_failed_results_for_one_case_open_one_failure(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)
    first_run_id = await seed_run(container, scenario)
    second_run_id = await seed_run(container, scenario)
    first = await seed_case_result(container, scenario, first_run_id, scenario.case, ResultStatus.FAILED)
    second = await seed_case_result(container, scenario, second_run_id, scenario.case, ResultStatus.FAILED)
    apply_case_result = ApplyCaseResultUseCase(
        container.database, SlowFailureRepository(container.failure_repository), container.failure_event_repository
    )

    await asyncio.gather(apply_case_result.handle(first), apply_case_result.handle(second))

    failures = await list_failure_rows(container, scenario.case.id)
    assert len(failures) == 1
    events = await list_event_rows(container, failures[0].id)
    assert sorted(event.kind for event in events) == sorted([FailureEventKind.OPENED, FailureEventKind.FAILED_AGAIN])
