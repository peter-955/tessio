from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.modules.labels.dependencies import get_create_label, get_delete_label, get_list_labels, get_update_label
from app.modules.labels.models.create_label_request import CreateLabelRequest
from app.modules.labels.models.label_response import LabelResponse
from app.modules.labels.models.update_label_request import UpdateLabelRequest
from app.modules.labels.usecases.create_label import CreateLabelUseCase
from app.modules.labels.usecases.delete_label import DeleteLabelUseCase
from app.modules.labels.usecases.list_labels import ListLabelsUseCase
from app.modules.labels.usecases.update_label import UpdateLabelUseCase
from app.modules.labels.utils.label_response import build_label_response
from app.modules.projects import get_signed_in_actor
from app.shared.permissions import Actor

labels_router = APIRouter(prefix="/api", tags=["labels"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]


@labels_router.get("/projects/{project_key}/labels")
async def list_labels(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListLabelsUseCase, Depends(get_list_labels)],
) -> list[LabelResponse]:
    return [build_label_response(summary) for summary in await use_case.execute(actor, project_key)]


@labels_router.post("/projects/{project_key}/labels", status_code=status.HTTP_201_CREATED)
async def create_label(
    project_key: str,
    body: CreateLabelRequest,
    actor: SignedInActor,
    use_case: Annotated[CreateLabelUseCase, Depends(get_create_label)],
) -> LabelResponse:
    return build_label_response(await use_case.execute(actor, project_key, body.name, body.color))


@labels_router.patch("/projects/{project_key}/labels/{label_id}")
async def update_label(
    project_key: str,
    label_id: UUID,
    body: UpdateLabelRequest,
    actor: SignedInActor,
    use_case: Annotated[UpdateLabelUseCase, Depends(get_update_label)],
) -> LabelResponse:
    return build_label_response(await use_case.execute(actor, project_key, label_id, body.name, body.color))


@labels_router.delete("/projects/{project_key}/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_label(
    project_key: str,
    label_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[DeleteLabelUseCase, Depends(get_delete_label)],
) -> None:
    await use_case.execute(actor, project_key, label_id)
