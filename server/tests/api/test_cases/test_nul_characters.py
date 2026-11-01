import pytest
from httpx import AsyncClient
from pydantic import JsonValue

from app.container import Container
from tests.api.test_cases.case_steps import (
    build_step,
    create_case,
    create_case_code,
    set_up_case_project,
    update_case,
)
from tests.conftest import RecordingMailer

TEXT_WITH_NUL = "Card\x00 accepted"
NUL_FIELDS: list[tuple[str, JsonValue]] = [
    ("businessValue", TEXT_WITH_NUL),
    ("preconditions", TEXT_WITH_NUL),
    ("steps", [build_step(TEXT_WITH_NUL, "Paid")]),
]


@pytest.mark.parametrize(("field_name", "value"), NUL_FIELDS)
async def test_a_new_case_with_a_nul_character_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, field_name: str, value: JsonValue
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)

    response = await create_case(client, case_project.key, case_project.story.jira_key, **{field_name: value})

    assert response.status_code == 422
    assert "NUL characters" in response.text


@pytest.mark.parametrize(("field_name", "value"), NUL_FIELDS)
async def test_a_case_edit_with_a_nul_character_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, field_name: str, value: JsonValue
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)
    case_code = await create_case_code(client, case_project.key, case_project.story.jira_key)

    response = await update_case(client, case_project.key, case_code, 1, **{field_name: value})

    assert response.status_code == 422
    assert "NUL characters" in response.text
