from uuid import UUID

from httpx import AsyncClient, Response

from app.shared.permissions import ProjectRole
from tests.api.test_data.conftest import DataTestContainer
from tests.api.test_data.environment_steps import create_data_item, create_environment
from tests.api.test_data.project_steps import SeededProject, seed_project, sign_up_member
from tests.conftest import RecordingMailer


async def set_up_qc(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> tuple[SeededProject, UUID]:
    project = await seed_project(data_container)
    user_id = await sign_up_member(client, data_container, recording_mailer, project, ProjectRole.QC)
    return project, user_id


async def list_descriptions(client: AsyncClient, project: SeededProject) -> dict[str, list[str | None]]:
    response = await client.get(f"/api/projects/{project.key}/test-data")
    assert response.status_code == 200, response.text
    descriptions: dict[str, list[str | None]] = {}
    for item in response.json():
        descriptions.setdefault(item["key"], []).append(item["description"])
    return descriptions


async def update(client: AsyncClient, project: SeededProject, item_id: str, **body: object) -> Response:
    return await client.put(
        f"/api/projects/{project.key}/test-data/{item_id}", json={"kind": "variable", "value": "x", **body}
    )


async def test_one_description_is_shared_by_every_value_of_a_key(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_qc(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project)

    created = await client.post(
        f"/api/projects/{project.key}/test-data",
        json={"key": "ADMIN_USER", "kind": "variable", "value": "admin", "description": "  Shop admin sign-in  "},
    )
    await create_data_item(client, project, "ADMIN_USER", "staging-admin", environment_id=environment_id)

    assert created.status_code == 201, created.text
    assert created.json()["description"] == "Shop admin sign-in"
    assert await list_descriptions(client, project) == {"ADMIN_USER": ["Shop admin sign-in", "Shop admin sign-in"]}


async def test_leaving_the_description_out_keeps_it_and_an_empty_one_clears_it(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_qc(client, data_container, recording_mailer)
    item_id = await create_data_item(client, project, "LOCALE", "fr")

    described = await update(client, project, item_id, key="LOCALE", description="Language of the shop")
    kept = await update(client, project, item_id, key="LOCALE")
    cleared = await update(client, project, item_id, key="LOCALE", description="   ")

    assert described.json()["description"] == "Language of the shop"
    assert kept.json()["description"] == "Language of the shop"
    assert cleared.json()["description"] is None


async def test_a_renamed_key_takes_its_description_along(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_qc(client, data_container, recording_mailer)
    item_id = await create_data_item(client, project, "LANG", "fr")
    await update(client, project, item_id, key="LANG", description="Language of the shop")

    renamed = await update(client, project, item_id, key="LOCALE")

    assert renamed.json()["description"] == "Language of the shop"
    assert await list_descriptions(client, project) == {"LOCALE": ["Language of the shop"]}


async def test_the_description_goes_with_the_last_value_of_its_key(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_qc(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project)
    project_item = await create_data_item(client, project, "LOCALE", "fr")
    environment_item = await create_data_item(client, project, "LOCALE", "en", environment_id=environment_id)
    await update(client, project, project_item, key="LOCALE", value="fr", description="Language")

    await client.delete(f"/api/projects/{project.key}/test-data/{project_item}")
    remaining = await list_descriptions(client, project)
    await client.delete(f"/api/projects/{project.key}/test-data/{environment_item}")
    await create_data_item(client, project, "LOCALE", "de")

    assert remaining == {"LOCALE": ["Language"]}
    assert await list_descriptions(client, project) == {"LOCALE": [None]}


async def test_a_description_over_500_characters_is_refused(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_qc(client, data_container, recording_mailer)

    response = await client.post(
        f"/api/projects/{project.key}/test-data",
        json={"key": "NOTE", "kind": "variable", "value": "x", "description": "d" * 501},
    )

    assert response.status_code == 422


async def test_the_endpoint_kind_no_longer_exists(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_qc(client, data_container, recording_mailer)

    response = await client.post(
        f"/api/projects/{project.key}/test-data",
        json={"key": "CHECKOUT", "kind": "endpoint", "value": "https://shop.test/checkout"},
    )

    assert response.status_code == 422
