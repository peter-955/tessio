from uuid import UUID

from app.modules.audit import AuditAction, RecordAuditEventUseCase
from app.modules.test_data.domains.data_item.repository import DataItemRepository
from app.modules.test_data.errors import DataItemNotFoundError, DataItemNotSecretError
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class RevealSecretUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        data_item_repository: DataItemRepository,
        secret_cipher: SecretCipher,
        record_audit_event: RecordAuditEventUseCase,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._data_item_repository = data_item_repository
        self._secret_cipher = secret_cipher
        self._record_audit_event = record_audit_event

    async def execute(self, actor: Actor, project_key: str, item_id: UUID) -> str:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.SECRET_REVEAL)
            item = await self._data_item_repository.find_by_id(access.project_id, item_id)
            if item is None:
                raise DataItemNotFoundError
            if not item.is_secret or item.value_encrypted is None:
                raise DataItemNotSecretError
            value = self._secret_cipher.decrypt(item.value_encrypted).decode()
            await self._record_audit_event.execute(
                actor.user_id,
                AuditAction.SECRET_REVEAL,
                access.project_id,
                item.id,
                api_token_id=actor.api_token_id,
            )
        return value
