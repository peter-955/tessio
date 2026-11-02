from collections.abc import Collection
from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert

from app.modules.labels.domains.label.entity import Label
from app.modules.labels.domains.test_case_labels.repository import TestCaseLabelRepository
from app.modules.labels.infrastructure.label_table import LabelTable
from app.modules.labels.infrastructure.test_case_label_table import TestCaseLabelTable
from app.shared.postgres import Database


class PostgresTestCaseLabelRepository(TestCaseLabelRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_for_case(self, test_case_id: UUID) -> list[Label]:
        labels_by_case_id = await self.list_for_cases([test_case_id])
        return labels_by_case_id.get(test_case_id, [])

    async def list_for_cases(self, test_case_ids: Collection[UUID]) -> dict[UUID, list[Label]]:
        if not test_case_ids:
            return {}
        result = await self._database.get_current_session().execute(
            select(TestCaseLabelTable.test_case_id, LabelTable)
            .join(LabelTable, LabelTable.id == TestCaseLabelTable.label_id)
            .where(TestCaseLabelTable.test_case_id.in_(sorted(test_case_ids)))
            .order_by(func.lower(LabelTable.name), LabelTable.id)
            .execution_options(populate_existing=True)
        )
        labels_by_case_id: dict[UUID, list[Label]] = {}
        for test_case_id, row in result:
            labels_by_case_id.setdefault(test_case_id, []).append(Label.model_validate(row))
        return labels_by_case_id

    async def replace_for_case(self, test_case_id: UUID, label_ids: Collection[UUID], linked_at: datetime) -> None:
        session = self._database.get_current_session()
        await session.execute(
            delete(TestCaseLabelTable).where(
                TestCaseLabelTable.test_case_id == test_case_id, TestCaseLabelTable.label_id.not_in(sorted(label_ids))
            )
        )
        if label_ids:
            await session.execute(
                insert(TestCaseLabelTable)
                .values(
                    [
                        {"test_case_id": test_case_id, "label_id": label_id, "created_at": linked_at}
                        for label_id in sorted(label_ids)
                    ]
                )
                .on_conflict_do_nothing()
            )
