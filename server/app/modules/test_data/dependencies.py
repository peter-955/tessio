from fastapi import Request

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


def get_list_environments(request: Request) -> ListEnvironmentsUseCase:
    use_case: ListEnvironmentsUseCase = request.app.state.container.list_environments
    return use_case


def get_create_environment(request: Request) -> CreateEnvironmentUseCase:
    use_case: CreateEnvironmentUseCase = request.app.state.container.create_environment
    return use_case


def get_update_environment(request: Request) -> UpdateEnvironmentUseCase:
    use_case: UpdateEnvironmentUseCase = request.app.state.container.update_environment
    return use_case


def get_archive_environment(request: Request) -> ArchiveEnvironmentUseCase:
    use_case: ArchiveEnvironmentUseCase = request.app.state.container.archive_environment
    return use_case


def get_unarchive_environment(request: Request) -> UnarchiveEnvironmentUseCase:
    use_case: UnarchiveEnvironmentUseCase = request.app.state.container.unarchive_environment
    return use_case


def get_delete_environment(request: Request) -> DeleteEnvironmentUseCase:
    use_case: DeleteEnvironmentUseCase = request.app.state.container.delete_environment
    return use_case


def get_list_data_items(request: Request) -> ListDataItemsUseCase:
    use_case: ListDataItemsUseCase = request.app.state.container.list_data_items
    return use_case


def get_list_effective_data_items(request: Request) -> ListEffectiveDataItemsUseCase:
    use_case: ListEffectiveDataItemsUseCase = request.app.state.container.list_effective_data_items
    return use_case


def get_create_data_item(request: Request) -> CreateDataItemUseCase:
    use_case: CreateDataItemUseCase = request.app.state.container.create_data_item
    return use_case


def get_update_data_item(request: Request) -> UpdateDataItemUseCase:
    use_case: UpdateDataItemUseCase = request.app.state.container.update_data_item
    return use_case


def get_delete_data_item(request: Request) -> DeleteDataItemUseCase:
    use_case: DeleteDataItemUseCase = request.app.state.container.delete_data_item
    return use_case


def get_reveal_secret(request: Request) -> RevealSecretUseCase:
    use_case: RevealSecretUseCase = request.app.state.container.reveal_secret
    return use_case


def get_preview_import(request: Request) -> PreviewImportUseCase:
    use_case: PreviewImportUseCase = request.app.state.container.preview_import
    return use_case


def get_commit_import(request: Request) -> CommitImportUseCase:
    use_case: CommitImportUseCase = request.app.state.container.commit_import
    return use_case
