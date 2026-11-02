from httpx import AsyncClient
from pydantic import JsonValue

from app.container import Container
from tests.api.runs.run_steps import seed_secret
from tests.api.shared_steps.shared_step_steps import (
    clear_saved_data_rows,
    create_case_with,
    create_shared_step_json,
    find_case_id,
    set_up_shared_step_project,
    update_shared_step,
)
from tests.api.test_cases.case_steps import change_status, create_case, get_case, seed_data_item, update_case
from tests.conftest import RecordingMailer

ROLE_ROWS: list[JsonValue] = [{"role": "admin"}, {"role": "viewer"}]


async def test_a_case_step_names_a_shared_step_and_keeps_its_data_keys(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    await create_shared_step_json(client, world.key)

    response = await create_case(
        client,
        world.key,
        world.story.jira_key,
        steps=[{"sharedStepKey": "LOG_IN"}, {"action": "Pay", "expected": "Paid"}],
        parameters=["role"],
        dataRows=ROLE_ROWS,
    )

    assert response.status_code == 201, response.text
    version = response.json()["currentVersion"]
    assert version["steps"] == [
        {"order": 1, "action": None, "expected": None, "sharedStepKey": "log_in"},
        {"order": 2, "action": "Pay", "expected": "Paid", "sharedStepKey": None},
    ]
    assert version["parameters"] == ["role"]
    assert version["dataRows"] == ROLE_ROWS
    assert version["dataKeys"] == ["base_url"]
    assert response.json()["unknownReferences"] == ["data.base_url"]


async def test_a_step_is_an_action_or_a_shared_step_never_both(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    await create_shared_step_json(client, world.key)

    both = await create_case(
        client, world.key, world.story.jira_key, steps=[{"action": "Sign in", "sharedStepKey": "log_in"}]
    )
    neither = await create_case(client, world.key, world.story.jira_key, steps=[{"expected": "Shown"}])

    assert both.status_code == 422
    assert both.json() == {
        "code": "INVALID_STEP_SHAPE",
        "message": "Step 1: a shared step has no action or expected result of its own.",
    }
    assert neither.status_code == 422
    assert neither.json() == {
        "code": "INVALID_STEP_SHAPE",
        "message": "Step 1: write the action, or pick a shared step.",
    }


async def test_an_unknown_or_archived_shared_step_is_refused_for_new_references(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    await create_shared_step_json(client, world.key)
    kept = await create_case_with(client, world.key, world.story.jira_key, steps=[{"sharedStepKey": "log_in"}])
    await update_shared_step(client, world.key, "log_in", 1, archived=True)

    unknown = await create_case(client, world.key, world.story.jira_key, steps=[{"sharedStepKey": "nope"}])
    archived = await create_case(client, world.key, world.story.jira_key, steps=[{"sharedStepKey": "log_in"}])
    kept_edit = await update_case(client, world.key, kept, 1, title="Still uses the archived step")

    assert unknown.status_code == 422
    assert unknown.json() == {
        "code": "UNKNOWN_SHARED_STEP",
        "message": "These shared steps do not exist or are archived: nope.",
    }
    assert archived.status_code == 422
    assert archived.json()["code"] == "UNKNOWN_SHARED_STEP"
    assert kept_edit.status_code == 200, kept_edit.text
    assert kept_edit.json()["currentVersion"]["number"] == 2


async def test_the_data_table_rules(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    story_key = world.story.jira_key
    steps: list[JsonValue] = [{"action": "Sign in as {{param.role}}"}]

    too_many_parameters = await create_case(
        client, world.key, story_key, steps=steps, parameters=[f"p{index}" for index in range(21)]
    )
    too_many_rows = await create_case(
        client, world.key, story_key, steps=steps, parameters=["role"], dataRows=[{"role": "x"}] * 21
    )
    wrong_row = await create_case(
        client, world.key, story_key, steps=steps, parameters=["role"], dataRows=[{"role": "a", "extra": "b"}]
    )
    rows_without_parameters = await create_case(client, world.key, story_key, steps=steps, dataRows=[{}])
    parameters_without_rows = await create_case(client, world.key, story_key, steps=steps, parameters=["role"])
    twice = await create_case(client, world.key, story_key, steps=steps, parameters=["role", "Role"])
    bad_name = await create_case(client, world.key, story_key, steps=steps, parameters=["the role"])
    largest = await create_case(
        client,
        world.key,
        story_key,
        steps=steps,
        parameters=[f"p{index}" for index in range(20)],
        dataRows=[{f"p{index}": str(row) for index in range(20)} for row in range(20)],
    )

    for response in (too_many_parameters, too_many_rows, wrong_row, rows_without_parameters, twice):
        assert response.status_code == 422, response.text
        assert response.json()["code"] == "INVALID_STEP_SHAPE"
    assert parameters_without_rows.status_code == 422
    assert parameters_without_rows.json() == {
        "code": "INVALID_STEP_SHAPE",
        "message": "Add at least one data row for the parameters, or remove the parameters.",
    }
    assert bad_name.status_code == 422
    assert bad_name.json()["detail"][0]["loc"] == ["body", "parameters", 0]
    assert largest.status_code == 201, largest.text


async def test_a_literal_secret_in_a_data_row_is_refused_but_a_reference_is_fine(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    await seed_secret(container, world.project, "admin_password", "Tr0ub4dor&3")
    story_key = world.story.jira_key
    steps: list[JsonValue] = [{"action": "Type {{param.password}}"}]

    literal = await create_case(
        client,
        world.key,
        story_key,
        steps=steps,
        parameters=["password"],
        dataRows=[{"password": "wrong"}, {"password": "my Tr0ub4dor&3"}],
    )
    reference = await create_case(
        client,
        world.key,
        story_key,
        steps=steps,
        parameters=["password"],
        dataRows=[{"password": "{{data.admin_password}}"}],
    )

    assert literal.status_code == 422
    assert literal.json()["code"] == "SECRET_IN_DATA_ROW"
    assert "row 2" in literal.json()["message"]
    assert "Tr0ub4dor" not in literal.json()["message"]
    assert reference.status_code == 201, reference.text
    assert reference.json()["currentVersion"]["dataKeys"] == ["admin_password"]
    assert reference.json()["unknownReferences"] == []


async def test_removing_every_data_row_but_keeping_the_parameters_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    code = await create_case_with(
        client,
        world.key,
        world.story.jira_key,
        steps=[{"action": "Sign in as {{param.role}}"}],
        parameters=["role"],
        dataRows=ROLE_ROWS,
    )

    without_rows = await update_case(client, world.key, code, 1, dataRows=[])
    without_both = await update_case(client, world.key, code, 1, parameters=[], dataRows=[])

    assert without_rows.status_code == 422
    assert without_rows.json()["code"] == "INVALID_STEP_SHAPE"
    assert without_both.status_code == 200, without_both.text
    assert without_both.json()["currentVersion"]["parameters"] == []


async def test_ready_needs_known_parameters_and_a_data_row(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    story_key = world.story.jira_key
    undeclared = await create_case_with(client, world.key, story_key, steps=[{"action": "Sign in as {{param.role}}"}])
    no_rows = await create_case_with(
        client,
        world.key,
        story_key,
        steps=[{"action": "Sign in as {{param.role}}"}],
        parameters=["role"],
        dataRows=ROLE_ROWS,
    )
    await clear_saved_data_rows(container, await find_case_id(client, world.key, no_rows))
    for code in (undeclared, no_rows):
        await change_status(client, world.key, code, "in_review")

    undeclared_detail = await get_case(client, world.key, undeclared)
    undeclared_ready = await change_status(client, world.key, undeclared, "ready")
    no_rows_ready = await change_status(client, world.key, no_rows, "ready")

    assert undeclared_detail.json()["unknownReferences"] == ["param.role"]
    assert undeclared_ready.status_code == 422
    assert undeclared_ready.json() == {"code": "UNKNOWN_REFERENCE", "message": "Unknown references: {{param.role}}."}
    assert no_rows_ready.status_code == 422
    assert no_rows_ready.json()["code"] == "INVALID_STEP_SHAPE"


async def test_a_shared_steps_unknown_data_key_blocks_ready(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    await create_shared_step_json(client, world.key)
    code = await create_case_with(
        client,
        world.key,
        world.story.jira_key,
        steps=[{"sharedStepKey": "log_in"}],
        parameters=["role"],
        dataRows=ROLE_ROWS,
    )
    await change_status(client, world.key, code, "in_review")

    refused = await change_status(client, world.key, code, "ready")
    await seed_data_item(container, world.project, "base_url")
    accepted = await change_status(client, world.key, code, "ready")

    assert refused.status_code == 422
    assert refused.json() == {"code": "UNKNOWN_REFERENCE", "message": "Unknown references: {{data.base_url}}."}
    assert accepted.status_code == 200, accepted.text


async def test_editing_the_data_rows_adds_a_version(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    code = await create_case_with(
        client,
        world.key,
        world.story.jira_key,
        steps=[{"action": "Sign in as {{param.role}}"}],
        parameters=["role"],
        dataRows=ROLE_ROWS,
    )

    response = await update_case(client, world.key, code, 1, dataRows=[{"role": "owner"}])

    assert response.status_code == 200, response.text
    version = response.json()["currentVersion"]
    assert version["number"] == 2
    assert version["parameters"] == ["role"]
    assert version["dataRows"] == [{"role": "owner"}]
