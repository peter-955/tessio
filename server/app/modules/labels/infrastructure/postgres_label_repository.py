from collections.abc import Collection
from uuid import UUID

from sqlalchemy import delete, func, select

from app.modules.labels.domains.label.entity import Label
from app.modules.labels.domains.label.repository import LabelRepository
from app.modules.labels.domains.label_summary.entity import LabelSummary
from app.modules.labels.infrastructure.label_table import LabelTable
from app.modules.labels.infrastructure.test_case_label_table import TestCaseLabelTable
from app.shared.postgres import Database


class PostgresLabelRepository(LabelRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_id(self, project_id: UUID, label_id: UUID) -> Label | None:
        row = await self._database.get_current_session().scalar(
            select(LabelTable)
            .where(LabelTable.project_id == project_id, LabelTable.id == label_id)
            .execution_options(populate_existing=True)
        )
        return None if row is None else Label.model_validate(row)

    async def find_by_name(self, project_id: UUID, name: str) -> Label | None:
        row = await self._database.get_current_session().scalar(
            select(LabelTable)
            .where(LabelTable.project_id == project_id, func.lower(LabelTable.name) == name.lower())
            .order_by(LabelTable.id)
            .limit(1)
            .execution_options(populate_existing=True)
        )
        return None if row is None else Label.model_validate(row)

    async def list_by_ids(self, project_id: UUID, label_ids: Collection[UUID]) -> list[Label]:
        if not label_ids:
            return []
        rows = await self._database.get_current_session().scalars(
            select(LabelTable)
            .where(LabelTable.project_id == project_id, LabelTable.id.in_(sorted(label_ids)))
            .order_by(func.lower(LabelTable.name), LabelTable.id)
            .execution_options(populate_existing=True)
        )
        return [Label.model_validate(row) for row in rows]

    async def list_summaries(self, project_id: UUID) -> list[LabelSummary]:
        case_counts = (
            select(TestCaseLabelTable.label_id, func.count().label("case_count"))
            .group_by(TestCaseLabelTable.label_id)
            .subquery()
        )
        result = await self._database.get_current_session().execute(
            select(LabelTable, func.coalesce(case_counts.c.case_count, 0))
            .outerjoin(case_counts, case_counts.c.label_id == LabelTable.id)
            .where(LabelTable.project_id == project_id)
            .order_by(func.lower(LabelTable.name), LabelTable.id)
            .execution_options(populate_existing=True)
        )
        return [LabelSummary(label=Label.model_validate(row), case_count=int(case_count)) for row, case_count in result]

    async def count_cases(self, label_id: UUID) -> int:
        count = await self._database.get_current_session().scalar(
            select(func.count()).select_from(TestCaseLabelTable).where(TestCaseLabelTable.label_id == label_id)
        )
        return int(count or 0)

    async def save(self, label: Label) -> None:
        await self._database.get_current_session().merge(LabelTable(**label.model_dump()))

    async def delete(self, label_id: UUID) -> None:
        session = self._database.get_current_session()
        await session.execute(delete(TestCaseLabelTable).where(TestCaseLabelTable.label_id == label_id))
        await session.execute(delete(LabelTable).where(LabelTable.id == label_id))
