from sqlalchemy import TableClause, Text, Uuid, column, table

SUITE_NAME_TABLE: TableClause = table("test_suites", column("id", Uuid), column("name", Text))
