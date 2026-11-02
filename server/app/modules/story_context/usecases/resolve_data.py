from uuid import UUID

from app.modules.audit import AuditAction, RecordAuditEventUseCase
from app.modules.story_context.domains.resolved_data.entity import ResolvedData
from app.modules.story_context.ports.run_scope_reader import RunScopeReader
from app.modules.story_context.ports.story_context_reader import StoryContextReader
from app.modules.story_context.utils.effective_data import select_effective_entries
from app.modules.story_context.utils.run_ownership import ensure_own_running_run
from app.modules.test_data import SecretValueReader
from app.shared.common import Transaction
from app.shared.permissions import (
    Actor,
    Capability,
    ProjectAccess,
    ProjectAccessResolver,
    ProjectNotFoundError,
    require,
)


class ResolveDataUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        run_scope_reader: RunScopeReader,
        story_context_reader: StoryContextReader,
        secret_value_reader: SecretValueReader,
        record_audit_event: RecordAuditEventUseCase,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._run_scope_reader = run_scope_reader
        self._story_context_reader = story_context_reader
        self._secret_value_reader = secret_value_reader
        self._record_audit_event = record_audit_event

    async def execute(self, actor: Actor, project_key: str, run_id: UUID, keys: list[str]) -> ResolvedData:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            return await self._resolve(access, actor, run_id, keys)

    async def execute_in_token_project(self, actor: Actor, run_id: UUID, keys: list[str]) -> ResolvedData:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve_by_id(actor, actor.token_project_id)
            return await self._resolve(access, actor, run_id, keys)

    async def _resolve(self, access: ProjectAccess, actor: Actor, run_id: UUID, keys: list[str]) -> ResolvedData:
        requested_keys = list(dict.fromkeys(key.strip() for key in keys))
        require(access, Capability.SECRET_USE_IN_RUN)
        run = ensure_own_running_run(await self._run_scope_reader.find_run(access.project_id, run_id), actor)
        run_data_keys = await self._run_scope_reader.list_data_keys(run.id)
        secret_values = await self._secret_value_reader.resolve_secrets(
            access.project_id, run.environment_id, [key for key in requested_keys if key in run_data_keys]
        )
        item_ids_by_key = {
            entry.key: entry.id
            for entry in select_effective_entries(
                await self._story_context_reader.list_data_entries(access.project_id), run.environment_id
            )
        }
        resolved_keys = [key for key in requested_keys if key in secret_values]
        for key in resolved_keys:
            await self._record_audit_event.execute(
                actor.user_id,
                AuditAction.SECRET_RESOLVE,
                access.project_id,
                item_ids_by_key.get(key),
                api_token_id=actor.api_token_id,
                run_id=run.id,
            )
        return ResolvedData(
            values={key: secret_values[key] for key in resolved_keys},
            unknown_keys=[key for key in requested_keys if key not in secret_values],
        )
