from uuid import uuid4

from httpx import AsyncClient

from app.container import Container
from app.modules.runs.infrastructure import (
    EmptyCriterionImpactCalculator,
    PostgresEnvironmentUsageChecker,
    PostgresRunningRunChecker,
    PostgresRunStoryReader,
)
from tests.api.runs.run_steps import finish, seed_environment, seed_runnable_story, sign_up_runner, start_run_id
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import read_tool_json


async def test_running_run_checker_sees_only_running_runs_of_the_story(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    story = await seed_runnable_story(container, project, runner.account.user_id)
    idle_story = await seed_runnable_story(container, project, runner.account.user_id)
    checker = PostgresRunningRunChecker(container.database)
    assert await checker.has_running_run(project.id, story.story_id) is False

    run_id = await start_run_id(client, runner.token, story.jira_key)

    assert await checker.has_running_run(project.id, story.story_id) is True
    assert await checker.has_running_run(project.id, idle_story.story_id) is False
    assert await checker.has_running_run(uuid4(), story.story_id) is False
    read_tool_json(await finish(client, runner.token, run_id))
    assert await checker.has_running_run(project.id, story.story_id) is False


async def test_environment_usage_checker_sees_any_run_on_the_environment(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    story = await seed_runnable_story(container, project, runner.account.user_id)
    unused_environment_id = await seed_environment(container, project, "Unused")
    checker = PostgresEnvironmentUsageChecker(container.database)
    assert await checker.is_used_by_runs(story.environment_id) is False

    run_id = await start_run_id(client, runner.token, story.jira_key, environment="Staging")
    read_tool_json(await finish(client, runner.token, run_id))

    assert await checker.is_used_by_runs(story.environment_id) is True
    assert await checker.is_used_by_runs(unused_environment_id) is False


async def test_run_story_reader_finds_the_jira_key(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    story = await seed_runnable_story(container, project, runner.account.user_id)

    async with container.database.begin():
        jira_key = await PostgresRunStoryReader(container.database).find_jira_key(story.story_id)

    assert jira_key == story.jira_key


async def test_empty_criterion_impact_calculator_returns_no_impacts() -> None:
    assert await EmptyCriterionImpactCalculator().calculate(uuid4(), uuid4()) == []
