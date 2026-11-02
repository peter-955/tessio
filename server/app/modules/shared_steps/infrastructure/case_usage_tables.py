from sqlalchemy import Integer, TableClause, Text, Uuid, column, table
from sqlalchemy.dialects.postgresql import JSONB

TEST_CASE_TABLE: TableClause = table(
    "test_cases",
    column("id", Uuid),
    column("project_id", Uuid),
    column("story_id", Uuid),
    column("number", Integer),
    column("title", Text),
    column("status", Text),
    column("current_version_id", Uuid),
)
TEST_CASE_VERSION_TABLE: TableClause = table(
    "test_case_versions", column("id", Uuid), column("number", Integer), column("steps", JSONB)
)
