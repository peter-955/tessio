from httpx import AsyncClient

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.labels.label_steps import create_label_id, set_case_labels
from tests.api.story_context.story_context_steps import add_token_holder
from tests.api.test_cases.case_steps import build_step, change_status, create_case_code, set_up_case_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool, read_tool_json


async def test_get_story_context_lists_each_cases_labels(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)
    smoke_id = await create_label_id(client, case_project.key, "Smoke")
    checkout_id = await create_label_id(client, case_project.key, "checkout")
    story_key = case_project.story.jira_key
    codes = []
    for title in ("Labelled", "Plain"):
        code = await create_case_code(client, case_project.key, story_key, title=title, steps=[build_step("Pay")])
        assert (await change_status(client, case_project.key, code, "in_review")).status_code == 200
        assert (await change_status(client, case_project.key, code, "ready")).status_code == 200
        codes.append(code)
    await set_case_labels(client, case_project.key, codes[0], [smoke_id, checkout_id])
    holder = await add_token_holder(client, container, recording_mailer, case_project.project, ProjectRole.DEV)

    response = await call_tool(client, holder.token, "get_story_context", {"story_key": story_key})

    cases = read_tool_json(response)["cases"]
    assert isinstance(cases, list)
    labels_by_code = {case["code"]: case.get("labels") for case in cases if isinstance(case, dict)}
    assert labels_by_code == {codes[0]: ["checkout", "Smoke"], codes[1]: None}
