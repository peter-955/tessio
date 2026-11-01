from httpx import AsyncClient

from app.container import Container
from tests.api.test_data.project_steps import seed_project, sign_up_member
from tests.conftest import RecordingMailer


async def test_a_nul_character_in_a_path_is_an_invalid_request(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_member(client, container, recording_mailer, project, None)

    response = await client.get("/api/projects/A%00B")

    assert response.status_code == 422
    assert response.json() == {
        "code": "INVALID_REQUEST",
        "message": "The request contains characters that are not allowed.",
    }
