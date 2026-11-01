from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.test_data.domains.data_item.repository import DataItemRepository
from app.modules.test_data.domains.environment.repository import EnvironmentRepository
from app.modules.test_data.domains.import_choice.entity import ImportChoice
from app.modules.test_data.domains.import_result.entity import ImportResult
from app.modules.test_data.errors import ImportKeyNotInFileError
from app.modules.test_data.ports.import_file_reader import ImportFileReader
from app.modules.test_data.typing.enums import ImportAction
from app.modules.test_data.utils.data_item_capability import require_data_item_edit
from app.modules.test_data.utils.data_item_value import apply_data_item_value, build_data_item
from app.modules.test_data.utils.environment_scope import require_writable_scope
from app.modules.test_data.utils.import_action import resolve_import_action
from app.modules.test_data.utils.import_file_loader import load_parsed_import
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class CommitImportUseCase:
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
        self,
        actor: Actor,
        project_key: str,
        file_id: UUID,
        environment_id: UUID | None,
        choices: Sequence[ImportChoice],
    ) -> ImportResult:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_DATA_EDIT)
            await require_writable_scope(self._environment_repository, access.project_id, environment_id)
            parsed_import = await load_parsed_import(
                self._import_file_reader, access.project_id, file_id, actor.user_id
            )
            value_by_key = {entry.key: entry.value for entry in parsed_import.entries}
            kind_by_key = {choice.key: choice.kind for choice in choices}
            if any(key not in value_by_key for key in kind_by_key):
                raise ImportKeyNotInFileError
            scope_items = {
                item.key: item
                for item in await self._data_item_repository.list_for_environment(access.project_id, environment_id)
                if item.environment_id == environment_id
            }
            require_data_item_edit(
                access,
                [*kind_by_key.values(), *(scope_items[key].kind for key in kind_by_key if key in scope_items)],
            )
            action_counts = dict.fromkeys(ImportAction, 0)
            now = datetime.now(UTC)
            for key, kind in kind_by_key.items():
                value = value_by_key[key]
                existing_item = scope_items.get(key)
                action = resolve_import_action(existing_item, kind, value, self._secret_cipher)
                action_counts[action] += 1
                if action is ImportAction.UNCHANGED:
                    continue
                item = (
                    build_data_item(
                        uuid7(), access.project_id, environment_id, key, kind, value, now, self._secret_cipher
                    )
                    if existing_item is None
                    else apply_data_item_value(existing_item, kind, value, self._secret_cipher)
                )
                await self._data_item_repository.save(item)
        return ImportResult(
            created=action_counts[ImportAction.CREATE],
            updated=action_counts[ImportAction.UPDATE],
            unchanged=action_counts[ImportAction.UNCHANGED],
        )
