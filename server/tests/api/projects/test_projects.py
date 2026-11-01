from httpx import AsyncClient

from app.container import Container
from app.modules.projects.infrastructure import StaticJiraConnectionChecker
from app.modules.users import WorkspaceRole
from tests.api.projects.user_steps import (
    build_create_project_body,
    generate_project_key,
    sign_up_as,
    use_session,
)
from tests.conftest import RecordingMailer


async def test_workspace_admin_creates_a_project_and_becomes_its_admin(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN, "Ada Admin")
    body = build_create_project_body()

    create_response = await client.post("/api/projects", json=body)
    members_response = await client.get(f"/api/projects/{body['key']}/members")

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["key"] == body["key"]
    assert created["jiraProjectKey"] == body["jiraProjectKey"]
    assert created["jiraBoardId"] == 7
    assert created["isArchived"] is False
    assert created["myRole"] == "admin"
    assert "image/png" in created["allowedFileTypes"]
    assert [(member["userId"], member["role"]) for member in members_response.json()] == [(str(admin.user_id), "admin")]


async def test_workspace_member_cannot_create_a_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)

    response = await client.post("/api/projects", json=build_create_project_body())

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


async def test_project_creation_needs_a_jira_connection(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    container.__dict__["jira_connection_checker"] = StaticJiraConnectionChecker(is_configured=False)
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)

    response = await client.post("/api/projects", json=build_create_project_body())

    assert response.status_code == 409
    assert response.json()["code"] == "JIRA_NOT_CONFIGURED"


async def test_duplicate_project_key_or_jira_project_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)
    body = build_create_project_body()
    await client.post("/api/projects", json=body)

    same_key_response = await client.post(
        "/api/projects", json=build_create_project_body(key=str(body["key"]), jira_project_key=generate_project_key())
    )
    same_jira_response = await client.post(
        "/api/projects", json=build_create_project_body(jira_project_key=str(body["jiraProjectKey"]))
    )

    assert same_key_response.status_code == 409
    assert same_key_response.json()["code"] == "PROJECT_KEY_ALREADY_USED"
    assert same_jira_response.status_code == 409
    assert same_jira_response.json()["code"] == "JIRA_PROJECT_ALREADY_LINKED"


async def test_invalid_project_key_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)

    lowercase_response = await client.post("/api/projects", json=build_create_project_body(key="shop"))
    too_long_response = await client.post("/api/projects", json=build_create_project_body(key="ABCDEFGHIJK"))

    assert lowercase_response.status_code == 422
    assert too_long_response.status_code == 422


async def test_blank_project_name_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)
    body = build_create_project_body()
    await client.post("/api/projects", json=body)

    create_response = await client.post("/api/projects", json={**build_create_project_body(), "name": "   "})
    blank_jira_key_response = await client.post(
        "/api/projects", json={**build_create_project_body(), "jiraProjectKey": "  "}
    )
    update_response = await client.patch(f"/api/projects/{body['key']}", json={"name": "  "})

    assert create_response.status_code == 422
    assert blank_jira_key_response.status_code == 422
    assert update_response.status_code == 422


async def test_project_shows_the_callers_role_and_capabilities(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    owner = await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)
    body = build_create_project_body()
    await client.post("/api/projects", json=body)
    viewer = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    use_session(client, owner.session_token)
    await client.put(f"/api/projects/{body['key']}/members/{viewer.user_id}", json={"role": "viewer"})
    use_session(client, viewer.session_token)

    response = await client.get(f"/api/projects/{body['key']}")

    assert response.status_code == 200
    assert response.json()["myRole"] == "viewer"
    assert "project.view" in response.json()["capabilities"]
    assert "api_token.create" in response.json()["capabilities"]
    assert "project.edit" not in response.json()["capabilities"]


async def test_non_member_cannot_see_the_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)
    body = build_create_project_body()
    await client.post("/api/projects", json=body)
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)

    get_response = await client.get(f"/api/projects/{body['key']}")
    patch_response = await client.patch(f"/api/projects/{body['key']}", json={"name": "Hidden"})
    list_response = await client.get("/api/projects")

    assert get_response.status_code == 404
    assert get_response.json()["code"] == "NOT_FOUND"
    assert patch_response.status_code == 404
    assert body["key"] not in [project["key"] for project in list_response.json()]


async def test_project_admin_edits_and_qc_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    owner = await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)
    body = build_create_project_body()
    await client.post("/api/projects", json=body)
    project_admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    tester = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    use_session(client, owner.session_token)
    await client.put(f"/api/projects/{body['key']}/members/{project_admin.user_id}", json={"role": "admin"})
    await client.put(f"/api/projects/{body['key']}/members/{tester.user_id}", json={"role": "qc"})

    use_session(client, project_admin.session_token)
    admin_response = await client.patch(
        f"/api/projects/{body['key']}",
        json={"name": "Renamed", "description": "", "jiraBoardId": 12, "allowedFileTypes": ["image/png", "text/csv"]},
    )
    use_session(client, tester.session_token)
    tester_response = await client.patch(f"/api/projects/{body['key']}", json={"name": "Nope"})

    assert admin_response.status_code == 200
    assert admin_response.json()["name"] == "Renamed"
    assert admin_response.json()["description"] is None
    assert admin_response.json()["jiraBoardId"] == 12
    assert admin_response.json()["allowedFileTypes"] == ["image/png", "text/csv"]
    assert admin_response.json()["key"] == body["key"]
    assert tester_response.status_code == 403
    assert tester_response.json()["code"] == "PERMISSION_DENIED"


async def test_invalid_file_type_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)
    body = build_create_project_body()
    await client.post("/api/projects", json=body)

    bad_type_response = await client.patch(f"/api/projects/{body['key']}", json={"allowedFileTypes": ["Not A Type"]})
    empty_response = await client.patch(f"/api/projects/{body['key']}", json={"allowedFileTypes": []})

    assert bad_type_response.status_code == 422
    assert empty_response.status_code == 422


async def test_only_workspace_admins_archive_and_unarchive(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    owner = await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)
    body = build_create_project_body()
    await client.post("/api/projects", json=body)
    project_admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    use_session(client, owner.session_token)
    await client.put(f"/api/projects/{body['key']}/members/{project_admin.user_id}", json={"role": "admin"})

    use_session(client, project_admin.session_token)
    refused_response = await client.post(f"/api/projects/{body['key']}/archive")
    use_session(client, owner.session_token)
    archive_response = await client.post(f"/api/projects/{body['key']}/archive")
    archive_again_response = await client.post(f"/api/projects/{body['key']}/archive")
    unarchive_response = await client.post(f"/api/projects/{body['key']}/unarchive")

    assert refused_response.status_code == 403
    assert archive_response.status_code == 200
    assert archive_response.json()["isArchived"] is True
    assert archive_response.json()["archivedAt"] is not None
    assert archive_again_response.json()["archivedAt"] == archive_response.json()["archivedAt"]
    assert unarchive_response.status_code == 200
    assert unarchive_response.json()["isArchived"] is False
    assert "project.edit" in unarchive_response.json()["capabilities"]


async def test_archived_project_is_read_only_and_hidden_from_the_default_list(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    owner = await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)
    body = build_create_project_body()
    await client.post("/api/projects", json=body)
    await client.post(f"/api/projects/{body['key']}/archive")

    get_response = await client.get(f"/api/projects/{body['key']}")
    patch_response = await client.patch(f"/api/projects/{body['key']}", json={"name": "Frozen"})
    put_member_response = await client.put(
        f"/api/projects/{body['key']}/members/{owner.user_id}", json={"role": "admin"}
    )
    default_list_response = await client.get("/api/projects")
    full_list_response = await client.get("/api/projects", params={"includeArchived": "true"})

    assert get_response.status_code == 200
    assert get_response.json()["capabilities"]
    assert "project.edit" not in get_response.json()["capabilities"]
    assert patch_response.status_code == 409
    assert patch_response.json()["code"] == "PROJECT_ARCHIVED"
    assert put_member_response.status_code == 409
    assert put_member_response.json()["code"] == "PROJECT_ARCHIVED"
    assert body["key"] not in [project["key"] for project in default_list_response.json()]
    assert body["key"] in [project["key"] for project in full_list_response.json()]


async def test_member_lists_only_their_projects(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    owner = await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)
    shared_body = build_create_project_body()
    private_body = build_create_project_body()
    await client.post("/api/projects", json=shared_body)
    await client.post("/api/projects", json=private_body)
    developer = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    use_session(client, owner.session_token)
    await client.put(f"/api/projects/{shared_body['key']}/members/{developer.user_id}", json={"role": "dev"})
    owner_list_response = await client.get("/api/projects")
    use_session(client, developer.session_token)

    developer_list_response = await client.get("/api/projects")

    owner_keys = [project["key"] for project in owner_list_response.json()]
    assert shared_body["key"] in owner_keys
    assert private_body["key"] in owner_keys
    assert [(project["key"], project["myRole"]) for project in developer_list_response.json()] == [
        (shared_body["key"], "dev")
    ]
