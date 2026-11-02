from collections.abc import Collection, Sequence
from datetime import datetime
from uuid import UUID, uuid7

from app.modules.test_cases.domains.test_case_content.entity import TestCaseContent
from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion
from app.modules.test_cases.utils.references import parse_references


def build_test_case_version(
    test_case_id: UUID,
    number: int,
    content: TestCaseContent,
    file_version_ids: Sequence[UUID],
    created_by: UUID,
    created_at: datetime,
    shared_data_keys: Collection[str] = (),
) -> TestCaseVersion:
    steps = [step.model_copy(update={"order": order}) for order, step in enumerate(content.steps, start=1)]
    references = parse_references(content.preconditions, steps, content.data_rows)
    return TestCaseVersion(
        id=uuid7(),
        test_case_id=test_case_id,
        number=number,
        title=content.title,
        priority=content.priority,
        business_value=content.business_value,
        preconditions=content.preconditions,
        steps=steps,
        criterion_ids=list(content.criterion_ids),
        data_keys=sorted(references.data_keys | set(shared_data_keys)),
        file_version_ids=list(file_version_ids),
        created_by=created_by,
        created_at=created_at,
        parameters=list(content.parameters),
        data_rows=[dict(row) for row in content.data_rows],
    )
