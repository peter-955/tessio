from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.test_cases.domains.linked_test_case.entity import LinkedTestCase
from app.modules.test_cases.domains.test_case.entity import TestCase
from app.modules.test_cases.domains.test_case_filter.entity import TestCaseFilter
from app.modules.test_cases.domains.test_case_summary.entity import TestCaseSummary
from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion


class TestCaseRepository(ABC):
    @abstractmethod
    async def find_by_number(self, project_id: UUID, number: int) -> TestCase | None: ...

    @abstractmethod
    async def find_by_number_for_update(self, project_id: UUID, number: int) -> TestCase | None: ...

    @abstractmethod
    async def list_summaries(self, project_id: UUID, case_filter: TestCaseFilter) -> list[TestCaseSummary]: ...

    @abstractmethod
    async def list_titles_for_stories(self, project_id: UUID, story_ids: frozenset[UUID]) -> set[tuple[UUID, str]]: ...

    @abstractmethod
    async def list_linked_to_criteria_for_update(
        self, project_id: UUID, criterion_ids: frozenset[UUID]
    ) -> list[LinkedTestCase]: ...

    @abstractmethod
    async def create(self, test_case: TestCase, version: TestCaseVersion) -> None: ...

    @abstractmethod
    async def add_version(self, test_case: TestCase, version: TestCaseVersion) -> None: ...

    @abstractmethod
    async def save(self, test_case: TestCase) -> None: ...
