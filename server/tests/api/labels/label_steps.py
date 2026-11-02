from httpx import AsyncClient, Response
from pydantic import JsonValue


async def create_label(client: AsyncClient, project_key: str, name: str, **fields: JsonValue) -> Response:
    return await client.post(f"/api/projects/{project_key}/labels", json={"name": name, **fields})


async def create_label_id(client: AsyncClient, project_key: str, name: str, **fields: JsonValue) -> str:
    response = await create_label(client, project_key, name, **fields)
    assert response.status_code == 201, response.text
    label_id: str = response.json()["id"]
    return label_id


async def list_labels(client: AsyncClient, project_key: str) -> list[dict[str, JsonValue]]:
    response = await client.get(f"/api/projects/{project_key}/labels")
    assert response.status_code == 200, response.text
    labels: list[dict[str, JsonValue]] = response.json()
    return labels


async def update_label(client: AsyncClient, project_key: str, label_id: str, **fields: JsonValue) -> Response:
    return await client.patch(f"/api/projects/{project_key}/labels/{label_id}", json=fields)


async def delete_label(client: AsyncClient, project_key: str, label_id: str) -> Response:
    return await client.delete(f"/api/projects/{project_key}/labels/{label_id}")


async def set_case_labels(client: AsyncClient, project_key: str, case_code: str, label_ids: list[str]) -> Response:
    return await client.put(
        f"/api/projects/{project_key}/test-cases/{case_code}/labels", json={"labelIds": list(label_ids)}
    )


async def list_case_codes(client: AsyncClient, project_key: str, labels: list[str]) -> list[str]:
    response = await client.get(f"/api/projects/{project_key}/test-cases", params={"label": labels})
    assert response.status_code == 200, response.text
    return [case["code"] for case in response.json()]
