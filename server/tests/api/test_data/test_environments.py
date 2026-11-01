from uuid import UUID

from httpx import AsyncClient
from sqlalchemy import text

from app.modules.projects.domains.project_changes.entity import ProjectChanges
from app.modules.test_data.infrastructure import StaticEnvironmentUsageChecker
from app.modules.users import build_actor
from app.shared.permissions import ProjectRole
from tests.api.test_data.conftest import DataTestContainer
from tests.api.test_data.environment_steps import create_data_item, create_environment
from tests.api.test_data.project_steps import SeededProject, add_member, seed_project, sign_up_member
from tests.conftest import RecordingMailer


async def set_up_admin(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> tuple[SeededProject, UUID]:
    project = await seed_project(data_container)
    user_id = await sign_up_member(client, data_container, recording_mailer, project, ProjectRole.ADMIN)
    return project, user_id


async def read_default_environment_id(data_container: DataTestContainer, project: SeededProject) -> UUID | None:
    async with data_container.database.begin():
        default_environment_id: UUID | None = await data_container.database.get_current_session().scalar(
            text("SELECT default_environment_id FROM projects WHERE id = :id"), {"id": project.id}
        )
    return default_environment_id


async def set_default_environment(
    data_container: DataTestContainer, project: SeededProject, user_id: UUID, environment_id: str
) -> None:
    async with data_container.database.begin():
        user = await data_container.user_repository.find_by_id(user_id)
    assert user is not None
    await data_container.update_project.execute(
        build_actor(user), project.key, ProjectChanges(default_environment_id=UUID(environment_id))
    )


async def test_create_list_and_replace_an_environment(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)

    created = await client.post(
        f"/api/projects/{project.key}/environments",
        json={"name": "  Staging  ", "baseUrl": "https://staging.shop.test", "healthCheckUrl": None},
    )
    await create_environment(client, project, name="dev", base_url="http://localhost:3000")

    assert created.status_code == 201
    body = created.json()
    assert body.keys() == {"id", "name", "baseUrl", "healthCheckUrl", "isArchived", "archivedAt", "createdAt"}
    assert body["name"] == "Staging"
    assert body["isArchived"] is False
    listed = await client.get(f"/api/projects/{project.key}/environments")
    assert [environment["name"] for environment in listed.json()] == ["dev", "Staging"]

    replaced = await client.put(
        f"/api/projects/{project.key}/environments/{body['id']}",
        json={"name": "staging", "baseUrl": "https://stage.shop.test", "healthCheckUrl": "https://stage.shop.test/up"},
    )

    assert replaced.status_code == 200
    assert replaced.json()["name"] == "staging"
    assert replaced.json()["baseUrl"] == "https://stage.shop.test"
    assert replaced.json()["healthCheckUrl"] == "https://stage.shop.test/up"
    assert replaced.json()["createdAt"] == body["createdAt"]


async def test_a_duplicate_name_is_refused_case_insensitively(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)
    await create_environment(client, project, name="Staging")
    other_id = await create_environment(client, project, name="QA")

    created = await client.post(
        f"/api/projects/{project.key}/environments", json={"name": "STAGING", "baseUrl": "https://x.test"}
    )
    renamed = await client.put(
        f"/api/projects/{project.key}/environments/{other_id}", json={"name": "staging", "baseUrl": "https://x.test"}
    )
    kept_own_name = await client.put(
        f"/api/projects/{project.key}/environments/{other_id}", json={"name": "qa", "baseUrl": "https://x.test"}
    )

    assert created.status_code == 409
    assert created.json()["code"] == "ENVIRONMENT_NAME_ALREADY_USED"
    assert renamed.status_code == 409
    assert renamed.json()["code"] == "ENVIRONMENT_NAME_ALREADY_USED"
    assert kept_own_name.status_code == 200


async def test_the_same_name_is_allowed_in_another_project(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_admin(client, data_container, recording_mailer)
    other_project = await seed_project(data_container)
    await add_member(data_container, other_project, user_id, ProjectRole.ADMIN)
    await create_environment(client, project, name="Staging")

    response = await client.post(
        f"/api/projects/{other_project.key}/environments", json={"name": "Staging", "baseUrl": "https://x.test"}
    )

    assert response.status_code == 201


async def test_bad_urls_and_names_are_refused(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)

    bodies = [
        {"name": "Staging", "baseUrl": "ftp://staging.shop.test"},
        {"name": "Staging", "baseUrl": "staging.shop.test"},
        {"name": "Staging", "baseUrl": "https://staging shop.test"},
        {"name": "Staging", "baseUrl": "https://staging.shop.test", "healthCheckUrl": "javascript:alert(1)"},
        {"name": "Staging", "baseUrl": "https://" + "a" * 2000},
        {"name": "   ", "baseUrl": "https://staging.shop.test"},
        {"name": "x" * 101, "baseUrl": "https://staging.shop.test"},
    ]
    responses = [await client.post(f"/api/projects/{project.key}/environments", json=body) for body in bodies]

    assert [response.status_code for response in responses] == [422] * len(bodies)


async def test_archive_hides_the_environment_and_clears_the_project_default(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_admin(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project)
    await set_default_environment(data_container, project, user_id, environment_id)
    assert await read_default_environment_id(data_container, project) == UUID(environment_id)

    archived = await client.post(f"/api/projects/{project.key}/environments/{environment_id}/archive")
    archived_again = await client.post(f"/api/projects/{project.key}/environments/{environment_id}/archive")

    assert archived.status_code == 200
    assert archived.json()["isArchived"] is True
    assert archived_again.json()["archivedAt"] == archived.json()["archivedAt"]
    assert await read_default_environment_id(data_container, project) is None
    assert (await client.get(f"/api/projects/{project.key}/environments")).json() == []
    listed_with_archived = await client.get(
        f"/api/projects/{project.key}/environments", params={"includeArchived": "true"}
    )
    assert [environment["id"] for environment in listed_with_archived.json()] == [environment_id]


async def test_unarchive_brings_the_environment_back(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project)
    await client.post(f"/api/projects/{project.key}/environments/{environment_id}/archive")

    unarchived = await client.post(f"/api/projects/{project.key}/environments/{environment_id}/unarchive")
    unarchived_again = await client.post(f"/api/projects/{project.key}/environments/{environment_id}/unarchive")

    assert unarchived.status_code == 200
    assert unarchived.json()["isArchived"] is False
    assert unarchived.json()["archivedAt"] is None
    assert unarchived_again.status_code == 200
    listed = await client.get(f"/api/projects/{project.key}/environments")
    assert [environment["id"] for environment in listed.json()] == [environment_id]


async def test_delete_removes_the_environment_and_its_rows_and_clears_the_default(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_admin(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project)
    await set_default_environment(data_container, project, user_id, environment_id)
    await create_data_item(client, project, "USER", "project-user")
    await create_data_item(client, project, "USER", "staging-user", environment_id=environment_id)
    await create_data_item(client, project, "TOKEN", "staging-token", kind="secret", environment_id=environment_id)

    response = await client.delete(f"/api/projects/{project.key}/environments/{environment_id}")

    assert response.status_code == 204
    assert (
        await client.get(f"/api/projects/{project.key}/environments", params={"includeArchived": "true"})
    ).json() == []
    items = (await client.get(f"/api/projects/{project.key}/test-data")).json()
    assert [(item["key"], item["environmentId"]) for item in items] == [("USER", None)]
    assert await read_default_environment_id(data_container, project) is None
    missing = await client.delete(f"/api/projects/{project.key}/environments/{environment_id}")
    assert missing.status_code == 404


async def test_delete_is_refused_while_runs_use_the_environment(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project)
    data_container.__dict__["environment_usage_checker"] = StaticEnvironmentUsageChecker(is_used=True)

    response = await client.delete(f"/api/projects/{project.key}/environments/{environment_id}")

    assert response.status_code == 409
    assert response.json() == {
        "code": "ENVIRONMENT_IN_USE",
        "message": "Runs use this environment; archive it instead.",
    }
    listed = await client.get(f"/api/projects/{project.key}/environments")
    assert [environment["id"] for environment in listed.json()] == [environment_id]


async def test_an_environment_of_another_project_is_not_found(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_admin(client, data_container, recording_mailer)
    other_project = await seed_project(data_container)
    await add_member(data_container, other_project, user_id, ProjectRole.ADMIN)
    foreign_environment_id = await create_environment(client, other_project)

    responses = [
        await client.put(
            f"/api/projects/{project.key}/environments/{foreign_environment_id}",
            json={"name": "Staging", "baseUrl": "https://x.test"},
        ),
        await client.post(f"/api/projects/{project.key}/environments/{foreign_environment_id}/archive"),
        await client.post(f"/api/projects/{project.key}/environments/{foreign_environment_id}/unarchive"),
        await client.delete(f"/api/projects/{project.key}/environments/{foreign_environment_id}"),
    ]

    assert [response.status_code for response in responses] == [404, 404, 404, 404]
    assert {response.json()["message"] for response in responses} == {"Environment not found."}
