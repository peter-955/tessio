from httpx import AsyncClient
from sqlalchemy import func, select

from app.container import Container
from app.modules.runs.infrastructure import CaseResultTable
from tests.api.runs.run_steps import read_tool_error, record_case, seed_runnable_story, sign_up_runner, start_run_id
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer


async def test_a_case_result_with_a_nul_character_is_a_tool_validation_error(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    story = await seed_runnable_story(container, project, runner.account.user_id, case_count=1, step_count=1)
    run_id = await start_run_id(client, runner.token, story.jira_key)

    response = await record_case(
        client,
        runner.token,
        run_id,
        story.case_ids[0],
        steps=[{"order": 1, "status": "passed", "actual_result": "Paid\x00 twice"}],
    )

    assert response.status_code == 200
    assert "NUL characters" in read_tool_error(response)
    async with container.database.begin():
        case_result_count = await container.database.get_current_session().scalar(
            select(func.count()).select_from(CaseResultTable).where(CaseResultTable.test_case_id == story.case_ids[0])
        )
    assert case_result_count == 0
