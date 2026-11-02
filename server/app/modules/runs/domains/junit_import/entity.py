from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run_counts.entity import RunCounts
from app.modules.runs.domains.unmapped_test.entity import UnmappedTest
from app.shared.common import Entity


class JunitImport(Entity):
    run: Run
    counts: RunCounts
    mapped_test_count: int
    unmapped_test_count: int
    unmapped_tests: list[UnmappedTest]
