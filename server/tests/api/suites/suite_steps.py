from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid7

from httpx import AsyncClient, Response
from sqlalchemy import func, insert, select, update

from app.container import Container
from app.modules.stories import SprintState
from app.modules.stories import TestStatus as StoryTestStatus
from app.modules.stories.infrastructure import AcceptanceCriterionTable, SprintTable, StoryTable
from app.modules.test_cases.infrastructure import TestCaseCriterionTable, TestCaseTable, TestCaseVersionTable
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import SeededStory, raise_gap_id
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import (
    Runner,
    SeededRunnableStory,
    build_steps,
    seed_runnable_story,
    sign_up_runner,
)
from tests.api.test_data.project_steps import SeededProject, seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool, read_tool_json

DEFAULT_SUITE_NAME = "Checkout regression"


@dataclass(frozen=True)
class SuiteWorld:
    project: SeededProject
    runner: Runner
    first_story: SeededRunnableStory
    second_story: SeededRunnableStory

    @property
    def key(self) -> str:
        return self.project.key

    @property
    def case_ids(self) -> list[UUID]:
        return [*self.first_story.case_ids, *self.second_story.case_ids]


async def seed_suite_world(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    role: ProjectRole = ProjectRole.QC,
    step_count: int = 2,
) -> SuiteWorld:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project, role)
    first_story = await seed_runnable_story(container, project, runner.account.user_id, 2, step_count)
    second_story = await seed_runnable_story(container, project, runner.account.user_id, 2, step_count)
    use_session(client, runner.account.session_token)
    return SuiteWorld(project=project, runner=runner, first_story=first_story, second_story=second_story)


async def create_suite(
    client: AsyncClient, project_key: str, name: str = DEFAULT_SUITE_NAME, **fields: object
) -> Response:
    return await client.post(f"/api/projects/{project_key}/suites", json={"name": name, **fields})


async def create_suite_id(client: AsyncClient, project_key: str, name: str = DEFAULT_SUITE_NAME) -> str:
    response = await create_suite(client, project_key, name)
    assert response.status_code == 201, response.text
    suite_id: str = response.json()["id"]
    return suite_id


async def set_suite_cases(client: AsyncClient, project_key: str, suite_id: str, case_ids: list[UUID]) -> Response:
    return await client.put(
        f"/api/projects/{project_key}/suites/{suite_id}/cases",
        json={"testCaseIds": [str(case_id) for case_id in case_ids]},
    )


async def add_cases_by_filter(client: AsyncClient, project_key: str, suite_id: str, **body: object) -> Response:
    return await client.post(f"/api/projects/{project_key}/suites/{suite_id}/cases/by-filter", json=body)


async def get_suite(client: AsyncClient, project_key: str, suite_id: str) -> Response:
    return await client.get(f"/api/projects/{project_key}/suites/{suite_id}")


async def seed_suite(
    client: AsyncClient, world: SuiteWorld, name: str = DEFAULT_SUITE_NAME, case_ids: list[UUID] | None = None
) -> str:
    suite_id = await create_suite_id(client, world.key, name)
    response = await set_suite_cases(client, world.key, suite_id, world.case_ids if case_ids is None else case_ids)
    assert response.status_code == 200, response.text
    return suite_id


async def archive_suite(client: AsyncClient, project_key: str, suite_id: str) -> Response:
    return await client.post(f"/api/projects/{project_key}/suites/{suite_id}/archive")


async def flag_needs_review(container: Container, test_case_id: UUID) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(TestCaseTable).where(TestCaseTable.id == test_case_id).values(needs_review_at=datetime.now(UTC))
        )


async def find_case_code(container: Container, test_case_id: UUID) -> str:
    async with container.database.begin():
        number = await container.database.get_current_session().scalar(
            select(TestCaseTable.number).where(TestCaseTable.id == test_case_id)
        )
    assert number is not None
    return f"TC-{number}"


async def find_story_test_status(container: Container, story_id: UUID) -> StoryTestStatus:
    async with container.database.begin():
        test_status = await container.database.get_current_session().scalar(
            select(StoryTable.test_status).where(StoryTable.id == story_id)
        )
    assert test_status is not None
    return test_status


async def set_story_test_status(container: Container, story_id: UUID, test_status: StoryTestStatus) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(StoryTable).where(StoryTable.id == story_id).values(test_status=test_status)
        )


async def put_story_test_status(client: AsyncClient, world: SuiteWorld, jira_key: str, test_status: str) -> Response:
    return await client.put(
        f"/api/projects/{world.key}/stories/{jira_key}/test-status", json={"testStatus": test_status}
    )


async def raise_story_gap(client: AsyncClient, world: SuiteWorld, story: SeededRunnableStory, **body: object) -> str:
    use_session(client, world.runner.account.session_token)
    return await raise_gap_id(
        client, world.key, SeededStory(id=story.story_id, jira_key=story.jira_key, criterion_ids={}), **body
    )


async def start_suite_run(client: AsyncClient, token: str, suite: str, **arguments: object) -> Response:
    return await call_tool(client, token, "start_run", {"suite": suite, **arguments})


async def start_suite_run_content(
    client: AsyncClient, token: str, suite: str, **arguments: object
) -> dict[str, object]:
    return read_tool_json(await start_suite_run(client, token, suite, **arguments))


async def record_suite_case(
    client: AsyncClient, token: str, run_id: str, case_id: UUID, status: str = "passed", step_count: int = 2
) -> Response:
    return await call_tool(
        client,
        token,
        "record_case_result",
        {
            "run_id": run_id,
            "case_id": str(case_id),
            "status": status,
            "duration_ms": 500,
            "steps": build_steps([status] * step_count),
        },
    )


async def start_manual_suite_run(client: AsyncClient, project_key: str, suite_id: str, **body: object) -> Response:
    return await client.post(f"/api/projects/{project_key}/runs", json={"suiteId": suite_id, **body})


async def set_priority(container: Container, test_case_id: UUID, priority: str) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(TestCaseTable).where(TestCaseTable.id == test_case_id).values(priority=priority)
        )


async def link_criterion(
    container: Container, story_id: UUID, case_ids: list[UUID], code: str = "AC-1", position: int = 1
) -> UUID:
    criterion_id = uuid7()
    now = datetime.now(UTC)
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(
            insert(AcceptanceCriterionTable).values(
                id=criterion_id,
                story_id=story_id,
                position=position,
                code=code,
                text=f"Criterion {code}",
                removed_at=None,
                created_at=now,
            )
        )
        for case_id in case_ids:
            await session.execute(
                insert(TestCaseCriterionTable).values(test_case_id=case_id, criterion_id=criterion_id, created_at=now)
            )
            version_id = await session.scalar(
                select(TestCaseTable.current_version_id).where(TestCaseTable.id == case_id)
            )
            await session.execute(
                update(TestCaseVersionTable)
                .where(TestCaseVersionTable.id == version_id)
                .values(criterion_ids=func.array_append(TestCaseVersionTable.criterion_ids, criterion_id))
            )
    return criterion_id


async def put_stories_in_active_sprint(container: Container, world: SuiteWorld) -> UUID:
    sprint_id = uuid7()
    now = datetime.now(UTC)
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(
            insert(SprintTable).values(
                id=sprint_id,
                project_id=world.project.id,
                jira_sprint_id=1,
                name="Sprint 1",
                state=SprintState.ACTIVE,
                start_at=now,
                end_at=None,
                complete_at=None,
                synced_at=now,
                created_at=now,
            )
        )
        await session.execute(
            update(StoryTable)
            .where(StoryTable.id.in_([world.first_story.story_id, world.second_story.story_id]))
            .values(sprint_id=sprint_id)
        )
    return sprint_id


async def run_suite_with(
    client: AsyncClient, world: SuiteWorld, statuses: list[str], suite: str = DEFAULT_SUITE_NAME
) -> str:
    content = read_tool_json(await start_suite_run(client, world.runner.token, suite))
    run_id = str(content["run_id"])
    for case_id, status in zip(world.case_ids, statuses, strict=False):
        read_tool_json(await record_suite_case(client, world.runner.token, run_id, case_id, status))
    return run_id


async def set_case_data_keys(container: Container, test_case_id: UUID, data_keys: list[str]) -> None:
    async with container.database.begin():
        session = container.database.get_current_session()
        version_id = await session.scalar(
            select(TestCaseTable.current_version_id).where(TestCaseTable.id == test_case_id)
        )
        await session.execute(
            update(TestCaseVersionTable).where(TestCaseVersionTable.id == version_id).values(data_keys=data_keys)
        )
