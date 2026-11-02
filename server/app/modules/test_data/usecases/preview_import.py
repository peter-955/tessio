from uuid import UUID

from app.modules.test_data.domains.data_item.repository import DataItemRepository
from app.modules.test_data.domains.environment.repository import EnvironmentRepository
from app.modules.test_data.domains.import_preview.entity import ImportPreview
from app.modules.test_data.domains.import_preview_item.entity import ImportPreviewItem
from app.modules.test_data.ports.import_file_reader import ImportFileReader
from app.modules.test_data.typing.enums import DataItemKind
from app.modules.test_data.utils.environment_scope import require_writable_scope
from app.modules.test_data.utils.import_action import resolve_import_action
from app.modules.test_data.utils.import_file_loader import load_parsed_import
from app.modules.test_data.utils.suggested_kind import suggest_kind
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class PreviewImportUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        environment_repository: EnvironmentRepository,
        data_item_repository: DataItemRepository,
        import_file_reader: ImportFileReader,
        secret_cipher: SecretCipher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._environment_repository = environment_repository
        self._data_item_repository = data_item_repository
        self._import_file_reader = import_file_reader
        self._secret_cipher = secret_cipher

    async def execute(
        self, actor: Actor, project_key: str, file_id: UUID, environment_id: UUID | None
    ) -> ImportPreview:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_DATA_EDIT)
            await require_writable_scope(self._environment_repository, access.project_id, environment_id)
            parsed_import = await load_parsed_import(
                self._import_file_reader, access.project_id, file_id, actor.user_id
            )
            scope_items = {
                item.key: item
                for item in await self._data_item_repository.list_for_environment(access.project_id, environment_id)
                if item.environment_id == environment_id
            }
        items = []
        for entry in parsed_import.entries:
            kind = suggest_kind(entry.key)
            items.append(
                ImportPreviewItem(
                    key=entry.key,
                    kind=kind,
                    value=None if kind is DataItemKind.SECRET else entry.value,
                    action=resolve_import_action(scope_items.get(entry.key), kind, entry.value, self._secret_cipher),
                    description=entry.description,
                )
            )
        return ImportPreview(format=parsed_import.format, items=items, skipped=parsed_import.skipped)
