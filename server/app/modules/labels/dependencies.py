from fastapi import Request

from app.modules.labels.usecases.create_label import CreateLabelUseCase
from app.modules.labels.usecases.delete_label import DeleteLabelUseCase
from app.modules.labels.usecases.list_labels import ListLabelsUseCase
from app.modules.labels.usecases.update_label import UpdateLabelUseCase


def get_list_labels(request: Request) -> ListLabelsUseCase:
    use_case: ListLabelsUseCase = request.app.state.container.list_labels
    return use_case


def get_create_label(request: Request) -> CreateLabelUseCase:
    use_case: CreateLabelUseCase = request.app.state.container.create_label
    return use_case


def get_update_label(request: Request) -> UpdateLabelUseCase:
    use_case: UpdateLabelUseCase = request.app.state.container.update_label
    return use_case


def get_delete_label(request: Request) -> DeleteLabelUseCase:
    use_case: DeleteLabelUseCase = request.app.state.container.delete_label
    return use_case
