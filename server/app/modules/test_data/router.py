from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.modules.projects import get_signed_in_actor
from app.modules.test_data.dependencies import (
    get_archive_environment,
    get_commit_import,
    get_create_data_item,
    get_create_environment,
    get_delete_data_item,
    get_delete_environment,
    get_list_data_items,
    get_list_effective_data_items,
    get_list_environments,
    get_preview_import,
    get_reveal_secret,
    get_unarchive_environment,
    get_update_data_item,
    get_update_environment,
)
from app.modules.test_data.domains.import_choice.entity import ImportChoice
from app.modules.test_data.models.create_data_item_request import CreateDataItemRequest
from app.modules.test_data.models.data_item_response import DataItemResponse
from app.modules.test_data.models.environment_request import EnvironmentRequest
from app.modules.test_data.models.environment_response import EnvironmentResponse
from app.modules.test_data.models.import_commit_request import ImportCommitRequest
from app.modules.test_data.models.import_preview_request import ImportPreviewRequest
from app.modules.test_data.models.import_preview_response import ImportPreviewResponse
from app.modules.test_data.models.import_result_response import ImportResultResponse
from app.modules.test_data.models.revealed_secret_response import RevealedSecretResponse
from app.modules.test_data.models.update_data_item_request import UpdateDataItemRequest
from app.modules.test_data.usecases.archive_environment import ArchiveEnvironmentUseCase
from app.modules.test_data.usecases.commit_import import CommitImportUseCase
from app.modules.test_data.usecases.create_data_item import CreateDataItemUseCase
from app.modules.test_data.usecases.create_environment import CreateEnvironmentUseCase
from app.modules.test_data.usecases.delete_data_item import DeleteDataItemUseCase
from app.modules.test_data.usecases.delete_environment import DeleteEnvironmentUseCase
from app.modules.test_data.usecases.list_data_items import ListDataItemsUseCase
from app.modules.test_data.usecases.list_effective_data_items import ListEffectiveDataItemsUseCase
from app.modules.test_data.usecases.list_environments import ListEnvironmentsUseCase
from app.modules.test_data.usecases.preview_import import PreviewImportUseCase
from app.modules.test_data.usecases.reveal_secret import RevealSecretUseCase
from app.modules.test_data.usecases.unarchive_environment import UnarchiveEnvironmentUseCase
from app.modules.test_data.usecases.update_data_item import UpdateDataItemUseCase
from app.modules.test_data.usecases.update_environment import UpdateEnvironmentUseCase
from app.modules.test_data.utils.data_item_response import build_data_item_response
from app.modules.test_data.utils.environment_response import build_environment_response
from app.modules.test_data.utils.import_responses import build_import_preview_response, build_import_result_response
from app.shared.permissions import Actor

test_data_router = APIRouter(prefix="/api", tags=["test-data"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]


@test_data_router.get("/projects/{project_key}/environments")
async def list_environments(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListEnvironmentsUseCase, Depends(get_list_environments)],
    include_archived: Annotated[bool, Query(alias="includeArchived")] = False,
) -> list[EnvironmentResponse]:
    environments = await use_case.execute(actor, project_key, include_archived)
    return [build_environment_response(environment) for environment in environments]


@test_data_router.post("/projects/{project_key}/environments", status_code=status.HTTP_201_CREATED)
async def create_environment(
    project_key: str,
    body: EnvironmentRequest,
    actor: SignedInActor,
    use_case: Annotated[CreateEnvironmentUseCase, Depends(get_create_environment)],
) -> EnvironmentResponse:
    environment = await use_case.execute(actor, project_key, body.name, body.base_url, body.health_check_url)
    return build_environment_response(environment)


@test_data_router.put("/projects/{project_key}/environments/{environment_id}")
async def update_environment(
    project_key: str,
    environment_id: UUID,
    body: EnvironmentRequest,
    actor: SignedInActor,
    use_case: Annotated[UpdateEnvironmentUseCase, Depends(get_update_environment)],
) -> EnvironmentResponse:
    environment = await use_case.execute(
        actor, project_key, environment_id, body.name, body.base_url, body.health_check_url
    )
    return build_environment_response(environment)


@test_data_router.post("/projects/{project_key}/environments/{environment_id}/archive")
async def archive_environment(
    project_key: str,
    environment_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[ArchiveEnvironmentUseCase, Depends(get_archive_environment)],
) -> EnvironmentResponse:
    return build_environment_response(await use_case.execute(actor, project_key, environment_id))


@test_data_router.post("/projects/{project_key}/environments/{environment_id}/unarchive")
async def unarchive_environment(
    project_key: str,
    environment_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[UnarchiveEnvironmentUseCase, Depends(get_unarchive_environment)],
) -> EnvironmentResponse:
    return build_environment_response(await use_case.execute(actor, project_key, environment_id))


@test_data_router.delete(
    "/projects/{project_key}/environments/{environment_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_environment(
    project_key: str,
    environment_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[DeleteEnvironmentUseCase, Depends(get_delete_environment)],
) -> None:
    await use_case.execute(actor, project_key, environment_id)


@test_data_router.get("/projects/{project_key}/test-data")
async def list_data_items(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListDataItemsUseCase, Depends(get_list_data_items)],
) -> list[DataItemResponse]:
    return [build_data_item_response(item) for item in await use_case.execute(actor, project_key)]


@test_data_router.get("/projects/{project_key}/test-data/effective")
async def list_effective_data_items(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListEffectiveDataItemsUseCase, Depends(get_list_effective_data_items)],
    environment_id: Annotated[UUID | None, Query(alias="environmentId")] = None,
) -> list[DataItemResponse]:
    return [build_data_item_response(item) for item in await use_case.execute(actor, project_key, environment_id)]


@test_data_router.post("/projects/{project_key}/test-data/import/preview")
async def preview_import(
    project_key: str,
    body: ImportPreviewRequest,
    actor: SignedInActor,
    use_case: Annotated[PreviewImportUseCase, Depends(get_preview_import)],
) -> ImportPreviewResponse:
    preview = await use_case.execute(actor, project_key, body.file_id, body.environment_id)
    return build_import_preview_response(preview)


@test_data_router.post("/projects/{project_key}/test-data/import/commit")
async def commit_import(
    project_key: str,
    body: ImportCommitRequest,
    actor: SignedInActor,
    use_case: Annotated[CommitImportUseCase, Depends(get_commit_import)],
) -> ImportResultResponse:
    choices = [ImportChoice(key=item.key, kind=item.kind) for item in body.items]
    result = await use_case.execute(actor, project_key, body.file_id, body.environment_id, choices)
    return build_import_result_response(result)


@test_data_router.post("/projects/{project_key}/test-data", status_code=status.HTTP_201_CREATED)
async def create_data_item(
    project_key: str,
    body: CreateDataItemRequest,
    actor: SignedInActor,
    use_case: Annotated[CreateDataItemUseCase, Depends(get_create_data_item)],
) -> DataItemResponse:
    item = await use_case.execute(actor, project_key, body.key, body.kind, body.value, body.environment_id)
    return build_data_item_response(item)


@test_data_router.put("/projects/{project_key}/test-data/{item_id}")
async def update_data_item(
    project_key: str,
    item_id: UUID,
    body: UpdateDataItemRequest,
    actor: SignedInActor,
    use_case: Annotated[UpdateDataItemUseCase, Depends(get_update_data_item)],
) -> DataItemResponse:
    item = await use_case.execute(actor, project_key, item_id, body.key, body.kind, body.value)
    return build_data_item_response(item)


@test_data_router.delete("/projects/{project_key}/test-data/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data_item(
    project_key: str,
    item_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[DeleteDataItemUseCase, Depends(get_delete_data_item)],
) -> None:
    await use_case.execute(actor, project_key, item_id)


@test_data_router.post("/projects/{project_key}/test-data/{item_id}/reveal")
async def reveal_secret(
    project_key: str,
    item_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[RevealSecretUseCase, Depends(get_reveal_secret)],
) -> RevealedSecretResponse:
    return RevealedSecretResponse(value=await use_case.execute(actor, project_key, item_id))
