import { TestCaseColumn } from "../enums/test-case-column.enum";
import type { TestCaseColumnDefinition } from "../types/test-case-column.type";

export const TEST_CASE_COLUMNS: TestCaseColumnDefinition[] = [
  { column: TestCaseColumn.CODE, namespace: "testCases", label: "code", isNumeric: false },
  { column: TestCaseColumn.TITLE, namespace: "testCases", label: "title", isNumeric: false },
  { column: TestCaseColumn.STORY, namespace: "testCases", label: "story", isNumeric: false },
  { column: TestCaseColumn.PRIORITY, namespace: "testCases", label: "priority", isNumeric: false },
  { column: TestCaseColumn.STATUS, namespace: "testCases", label: "status", isNumeric: false },
  {
    column: TestCaseColumn.LATEST_RESULT,
    namespace: "traceability",
    label: "latestResult",
    isNumeric: false,
  },
  { column: TestCaseColumn.STEPS, namespace: "testCases", label: "steps", isNumeric: true },
  { column: TestCaseColumn.CRITERIA, namespace: "testCases", label: "criteria", isNumeric: true },
  {
    column: TestCaseColumn.LAST_SAVED,
    namespace: "testCases",
    label: "lastSaved",
    isNumeric: false,
  },
];
