from uuid import UUID

from app.modules.test_cases.domains.test_case.entity import TestCase
from app.shared.common import Entity


class LinkedTestCase(Entity):
    test_case: TestCase
    linked_criterion_ids: frozenset[UUID]
