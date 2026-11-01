from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from app.shared.events import LiveEventType
from tests.api.projects.user_steps import (
    build_create_project_body,
    create_invited_user,
    deactivate_user,
    sign_up_as,
    use_session,
)
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def create_project_as_owner(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> tuple[str, str]:
    owner = await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER, "Olivia Owner")
    body = build_create_project_body()
    response = await client.post("/api/projects", json=body)
    assert response.status_code == 201
    return str(body["key"]), owner.session_token


async def test_member_is_added_then_their_role_changes(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project_key, owner_token = await create_project_as_owner(client, container, recording_mailer)
    analyst = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER, "Bea Analyst")
    use_session(client, owner_token)

    add_response = await client.put(f"/api/projects/{project_key}/members/{analyst.user_id}", json={"role": "ba"})
    change_response = await client.put(f"/api/projects/{project_key}/members/{analyst.user_id}", json={"role": "pm"})
    members_response = await client.get(f"/api/projects/{project_key}/members")

    assert add_response.status_code == 200
    assert add_response.json()["role"] == "ba"
    assert add_response.json()["email"] == analyst.email
    assert add_response.json()["userStatus"] == "active"
    assert change_response.json()["role"] == "pm"
    assert change_response.json()["addedAt"] == add_response.json()["addedAt"]
    roles_by_user_id = {member["userId"]: member["role"] for member in members_response.json()}
    assert roles_by_user_id[str(analyst.user_id)] == "pm"
    assert len(roles_by_user_id) == 2


async def test_invited_user_can_be_added(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project_key, _ = await create_project_as_owner(client, container, recording_mailer)
    invited_user_id = await create_invited_user(container, recording_mailer)

    response = await client.put(f"/api/projects/{project_key}/members/{invited_user_id}", json={"role": "dev"})

    assert response.status_code == 200
    assert response.json()["userStatus"] == "invited"


async def test_deactivated_user_cannot_be_added_but_can_be_removed(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project_key, _ = await create_project_as_owner(client, container, recording_mailer)
    leaving_user_id = await create_invited_user(container, recording_mailer)
    other_user_id = await create_invited_user(container, recording_mailer)
    await client.put(f"/api/projects/{project_key}/members/{leaving_user_id}", json={"role": "qc"})
    await deactivate_user(container, leaving_user_id)
    await deactivate_user(container, other_user_id)

    add_response = await client.put(f"/api/projects/{project_key}/members/{other_user_id}", json={"role": "qc"})
    remove_response = await client.delete(f"/api/projects/{project_key}/members/{leaving_user_id}")

    assert add_response.status_code == 409
    assert add_response.json()["code"] == "USER_DEACTIVATED"
    assert remove_response.status_code == 204


async def test_unknown_user_cannot_be_added(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project_key, _ = await create_project_as_owner(client, container, recording_mailer)

    response = await client.put(
        f"/api/projects/{project_key}/members/00000000-0000-7000-8000-000000000000", json={"role": "qc"}
    )

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


async def test_last_project_admin_cannot_be_demoted_or_removed(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    owner = await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)
    body = build_create_project_body()
    await client.post("/api/projects", json=body)
    second_admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    use_session(client, owner.session_token)
    project_key = body["key"]

    demote_response = await client.put(f"/api/projects/{project_key}/members/{owner.user_id}", json={"role": "qc"})
    remove_response = await client.delete(f"/api/projects/{project_key}/members/{owner.user_id}")
    await client.put(f"/api/projects/{project_key}/members/{second_admin.user_id}", json={"role": "admin"})
    demote_with_second_admin_response = await client.put(
        f"/api/projects/{project_key}/members/{owner.user_id}", json={"role": "qc"}
    )
    use_session(client, second_admin.session_token)
    self_demote_response = await client.put(
        f"/api/projects/{project_key}/members/{second_admin.user_id}", json={"role": "viewer"}
    )

    assert demote_response.status_code == 409
    assert demote_response.json()["code"] == "LAST_PROJECT_ADMIN"
    assert remove_response.status_code == 409
    assert remove_response.json()["code"] == "LAST_PROJECT_ADMIN"
    assert demote_with_second_admin_response.status_code == 200
    assert self_demote_response.status_code == 409
    assert self_demote_response.json()["code"] == "LAST_PROJECT_ADMIN"


async def test_removing_a_non_member_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project_key, _ = await create_project_as_owner(client, container, recording_mailer)
    outsider_id = await create_invited_user(container, recording_mailer)

    response = await client.delete(f"/api/projects/{project_key}/members/{outsider_id}")

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


async def test_candidates_exclude_members_and_deactivated_users_and_match_the_query(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project_key, _ = await create_project_as_owner(client, container, recording_mailer)
    marker = project_key.lower()
    member_id = await create_invited_user(container, recording_mailer, f"Member {marker}")
    deactivated_id = await create_invited_user(container, recording_mailer, f"Gone {marker}")
    candidate_id = await create_invited_user(container, recording_mailer, f"Candidate {marker}")
    await create_invited_user(container, recording_mailer, "Unrelated Person")
    await client.put(f"/api/projects/{project_key}/members/{member_id}", json={"role": "viewer"})
    await deactivate_user(container, deactivated_id)

    query_response = await client.get(f"/api/projects/{project_key}/members/candidates", params={"query": marker})
    wildcard_response = await client.get(f"/api/projects/{project_key}/members/candidates", params={"query": "%"})
    all_response = await client.get(f"/api/projects/{project_key}/members/candidates")

    assert query_response.status_code == 200
    assert [candidate["userId"] for candidate in query_response.json()] == [str(candidate_id)]
    assert query_response.json()[0]["userStatus"] == "invited"
    assert wildcard_response.json() == []
    all_candidate_ids = [candidate["userId"] for candidate in all_response.json()]
    assert len(all_candidate_ids) <= 20
    assert str(member_id) not in all_candidate_ids
    assert str(deactivated_id) not in all_candidate_ids


async def test_member_without_member_management_cannot_manage_members(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project_key, owner_token = await create_project_as_owner(client, container, recording_mailer)
    tester = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    use_session(client, owner_token)
    await client.put(f"/api/projects/{project_key}/members/{tester.user_id}", json={"role": "qc"})
    use_session(client, tester.session_token)

    candidates_response = await client.get(f"/api/projects/{project_key}/members/candidates")
    put_response = await client.put(f"/api/projects/{project_key}/members/{tester.user_id}", json={"role": "admin"})
    members_response = await client.get(f"/api/projects/{project_key}/members")

    assert candidates_response.status_code == 403
    assert candidates_response.json()["code"] == "PERMISSION_DENIED"
    assert put_response.status_code == 403
    assert members_response.status_code == 200


async def test_non_member_cannot_list_members(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project_key, _ = await create_project_as_owner(client, container, recording_mailer)
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)

    response = await client.get(f"/api/projects/{project_key}/members")

    assert response.status_code == 404


async def test_member_changes_publish_a_members_changed_event(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project_key, _ = await create_project_as_owner(client, container, recording_mailer)
    project_id = (await client.get(f"/api/projects/{project_key}")).json()["id"]
    developer_id = await create_invited_user(container, recording_mailer)

    await client.put(f"/api/projects/{project_key}/members/{developer_id}", json={"role": "dev"})
    await client.delete(f"/api/projects/{project_key}/members/{developer_id}")

    assert [(event.type, str(event.project_id)) for event in recording_live_event_publisher.events] == [
        (LiveEventType.PROJECT_MEMBERS_CHANGED, project_id),
        (LiveEventType.PROJECT_MEMBERS_CHANGED, project_id),
    ]
