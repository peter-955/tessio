from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid7

from httpx import AsyncClient, Response
from sqlalchemy import insert, select

from app.container import Container
from app.modules.runs import ResultStatus, RunExecutor, RunStatus
from app.modules.runs.infrastructure import CaseResultTable, RunTable
from app.modules.test_cases.infrastructure import TestCaseTable
from app.modules.test_data.infrastructure import EnvironmentTable
from tests.api.test_cases.case_steps import CaseProject, build_step, create_case_code


@dataclass(frozen=True)
class FlakyCase:
    case_project: CaseProject
    code: str
    test_case_id: UUID
    environment_id: UUID

    @property
    def key(self) -> str:
        return self.case_project.key


async def seed_environment(container: Container, project_id: UUID) -> UUID:
    environment_id = uuid7()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(EnvironmentTable).values(
                id=environment_id,
                project_id=project_id,
                name=f"Staging {environment_id.hex[-12:]}",
                base_url="https://staging.shop.test",
                health_check_url=None,
                archived_at=None,
                created_at=datetime.now(UTC),
            )
        )
    return environment_id


async def find_case_ids(container: Container, project_id: UUID, code: str) -> tuple[UUID, UUID]:
    number = int(code.removeprefix("TC-"))
    async with container.database.begin():
        row = (
            await container.database.get_current_session().execute(
                select(TestCaseTable.id, TestCaseTable.current_version_id).where(
                    TestCaseTable.project_id == project_id, TestCaseTable.number == number
                )
            )
        ).one()
    test_case_id, version_id = row
    assert version_id is not None
    return test_case_id, version_id


async def create_flaky_case(client: AsyncClient, container: Container, case_project: CaseProject) -> FlakyCase:
    code = await create_case_code(client, case_project.key, case_project.story.jira_key, steps=[build_step("Pay")])
    test_case_id, _ = await find_case_ids(container, case_project.project.id, code)
    environment_id = await seed_environment(container, case_project.project.id)
    return FlakyCase(case_project=case_project, code=code, test_case_id=test_case_id, environment_id=environment_id)


async def seed_result(
    container: Container,
    flaky_case: FlakyCase,
    status: ResultStatus,
    recorded_at: datetime,
    executor: RunExecutor = RunExecutor.CLAUDE,
    version_id: UUID | None = None,
) -> UUID:
    if version_id is None:
        _, version_id = await find_case_ids(container, flaky_case.case_project.project.id, flaky_case.code)
    run_id = uuid7()
    case_result_id = uuid7()
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(
            insert(RunTable).values(
                id=run_id,
                project_id=flaky_case.case_project.project.id,
                story_id=flaky_case.case_project.story.id,
                environment_id=flaky_case.environment_id,
                executor=executor,
                status=RunStatus.PASSED if status is ResultStatus.PASSED else RunStatus.FAILED,
                abort_reason=None,
                parent_run_id=None,
                started_by=flaky_case.case_project.user_id,
                started_via_token_id=None,
                summary=None,
                report=None,
                started_at=recorded_at,
                last_activity_at=recorded_at,
                finished_at=recorded_at,
                created_at=recorded_at,
            )
        )
        await session.execute(
            insert(CaseResultTable).values(
                id=case_result_id,
                run_id=run_id,
                test_case_id=flaky_case.test_case_id,
                test_case_version_id=version_id,
                status=status,
                duration_ms=900,
                suspected_cause=None,
                cause_reason=None,
                recorded_by=flaky_case.case_project.user_id,
                created_at=recorded_at,
            )
        )
    return case_result_id


async def seed_history(
    container: Container, flaky_case: FlakyCase, outcomes: str, newest_at: datetime | None = None
) -> None:
    newest = newest_at or datetime.now(UTC)
    for index, outcome in enumerate(outcomes):
        status = ResultStatus.PASSED if outcome == "P" else ResultStatus.FAILED
        await seed_result(container, flaky_case, status, newest - timedelta(minutes=index))


async def recompute(container: Container, flaky_case: FlakyCase) -> None:
    await container.recompute_flaky.execute(flaky_case.test_case_id)


async def get_case_json(client: AsyncClient, flaky_case: FlakyCase) -> dict[str, object]:
    response = await client.get(f"/api/projects/{flaky_case.key}/test-cases/{flaky_case.code}")
    assert response.status_code == 200, response.text
    body: dict[str, object] = response.json()
    return body


async def list_case_codes(client: AsyncClient, project_key: str, **filters: str) -> list[str]:
    response = await client.get(f"/api/projects/{project_key}/test-cases", params=filters)
    assert response.status_code == 200, response.text
    return [case["code"] for case in response.json()]


async def quarantine(client: AsyncClient, flaky_case: FlakyCase, reason: str | None = None) -> Response:
    body: dict[str, object] = {} if reason is None else {"reason": reason}
    return await client.put(f"/api/projects/{flaky_case.key}/test-cases/{flaky_case.code}/quarantine", json=body)


async def release(client: AsyncClient, flaky_case: FlakyCase) -> Response:
    return await client.delete(f"/api/projects/{flaky_case.key}/test-cases/{flaky_case.code}/quarantine")


async def list_quarantine_events(client: AsyncClient, flaky_case: FlakyCase) -> list[dict[str, object]]:
    response = await client.get(f"/api/projects/{flaky_case.key}/test-cases/{flaky_case.code}/quarantine-events")
    assert response.status_code == 200, response.text
    events: list[dict[str, object]] = response.json()
    return events
