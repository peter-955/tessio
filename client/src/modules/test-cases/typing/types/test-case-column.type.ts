import type { TestCaseColumn } from "../enums/test-case-column.enum";

export type TestCaseColumnLabel =
  "code" | "title" | "story" | "priority" | "status" | "steps" | "criteria" | "lastSaved";

export type TestCaseColumnDefinition =
  | {
      column: Exclude<TestCaseColumn, TestCaseColumn.LATEST_RESULT>;
      namespace: "testCases";
      label: TestCaseColumnLabel;
      isNumeric: boolean;
    }
  | {
      column: TestCaseColumn.LATEST_RESULT;
      namespace: "traceability";
      label: "latestResult";
      isNumeric: false;
    };
