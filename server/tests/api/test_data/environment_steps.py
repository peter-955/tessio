from httpx import AsyncClient

from tests.api.test_data.project_steps import SeededProject


async def create_environment(
    client: AsyncClient,
    project: SeededProject,
    name: str = "Staging",
    base_url: str = "https://staging.shop.test",
    health_check_url: str | None = None,
) -> str:
    response = await client.post(
        f"/api/projects/{project.key}/environments",
        json={"name": name, "baseUrl": base_url, "healthCheckUrl": health_check_url},
    )
    assert response.status_code == 201, response.text
    return str(response.json()["id"])


async def create_data_item(
    client: AsyncClient,
    project: SeededProject,
    key: str,
    value: str,
    kind: str = "variable",
    environment_id: str | None = None,
) -> str:
    response = await client.post(
        f"/api/projects/{project.key}/test-data",
        json={"key": key, "kind": kind, "value": value, "environmentId": environment_id},
    )
    assert response.status_code == 201, response.text
    return str(response.json()["id"])
