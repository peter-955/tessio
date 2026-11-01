from datetime import timedelta
from uuid import uuid7

from httpx import AsyncClient

from app.container import Container
from app.modules.insights import LatestResultCriterionImpactCalculator
from app.modules.insights.infrastructure import PostgresCoverageReader
from app.modules.runs import CriterionImpact, CriterionStatus, ResultStatus, RunStatus
from app.modules.test_cases import TestCaseStatus as CaseStatus
from tests.api.insights.insight_steps import (
    BASE_TIME,
    remove_criterion,
    seed_case,
    seed_result,
    seed_run,
    seed_story,
    sign_in_world,
)
from tests.conftest import RecordingMailer


def build_calculator(container: Container) -> LatestResultCriterionImpactCalculator:
    return LatestResultCriterionImpactCalculator(container.database, PostgresCoverageReader(container.database))


async def test_impact_gives_status_and_case_codes_after_the_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    story = await seed_story(container, world, criterion_codes=("AC1", "AC2", "AC3", "AC4", "AC5"))
    await remove_criterion(container, story.criterion_ids["AC5"])
    passing_case = await seed_case(container, world, story, criterion_codes=("AC1", "AC2"))
    failing_case = await seed_case(container, world, story, criterion_codes=("AC2",))
    blocked_case = await seed_case(container, world, story, criterion_codes=("AC3",))
    earlier_case = await seed_case(container, world, story, criterion_codes=("AC3",))
    await seed_case(container, world, story, CaseStatus.DEPRECATED, ("AC4",))
    earlier_run = await seed_run(container, world, story, (earlier_case,), RunStatus.PASSED, BASE_TIME)
    await seed_result(container, world, earlier_run, earlier_case, ResultStatus.PASSED, BASE_TIME)
    run_at = BASE_TIME + timedelta(hours=1)
    run_id = await seed_run(
        container, world, story, (passing_case, failing_case, blocked_case), RunStatus.RUNNING, run_at
    )
    await seed_result(container, world, run_id, passing_case, ResultStatus.PASSED, run_at)
    await seed_result(container, world, run_id, failing_case, ResultStatus.FAILED, run_at)
    await seed_result(container, world, run_id, blocked_case, ResultStatus.BLOCKED, run_at)

    async with container.database.begin():
        impacts = await build_calculator(container).calculate(world.project.id, run_id)

    assert impacts == [
        CriterionImpact(
            criterion_id=story.criterion_ids["AC1"],
            code="AC1",
            text="Criterion AC1",
            status=CriterionStatus.PASSED,
            run_case_codes=[passing_case.code],
            failed_case_codes=[],
        ),
        CriterionImpact(
            criterion_id=story.criterion_ids["AC2"],
            code="AC2",
            text="Criterion AC2",
            status=CriterionStatus.FAILED,
            run_case_codes=[passing_case.code, failing_case.code],
            failed_case_codes=[failing_case.code],
        ),
        CriterionImpact(
            criterion_id=story.criterion_ids["AC3"],
            code="AC3",
            text="Criterion AC3",
            status=CriterionStatus.BLOCKED,
            run_case_codes=[blocked_case.code],
            failed_case_codes=[blocked_case.code],
        ),
        CriterionImpact(
            criterion_id=story.criterion_ids["AC4"],
            code="AC4",
            text="Criterion AC4",
            status=CriterionStatus.UNCOVERED,
            run_case_codes=[],
            failed_case_codes=[],
        ),
    ]


async def test_case_without_result_in_the_run_is_listed_but_not_failed(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    story = await seed_story(container, world, criterion_codes=("AC1",))
    case = await seed_case(container, world, story, criterion_codes=("AC1",))
    run_id = await seed_run(container, world, story, (case,), RunStatus.RUNNING)

    impacts = await build_calculator(container).calculate(world.project.id, run_id)

    assert [(impact.status, impact.run_case_codes, impact.failed_case_codes) for impact in impacts] == [
        (CriterionStatus.NOT_RUN, [case.code], [])
    ]


async def test_unknown_or_foreign_run_gives_no_impact(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    other_world = await sign_in_world(client, container, recording_mailer)
    other_story = await seed_story(container, other_world, criterion_codes=("AC1",))
    other_run_id = await seed_run(container, other_world, other_story)
    world = await sign_in_world(client, container, recording_mailer)
    calculator = build_calculator(container)

    assert await calculator.calculate(world.project.id, uuid7()) == []
    assert await calculator.calculate(world.project.id, other_run_id) == []
