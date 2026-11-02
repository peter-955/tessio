import englishFailures from "@/lib/i18n/locales/en/failures.json";
import { screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CASE_RESULT_ID, RUN_ID } from "../../test/utils/failure-fixture.util";
import { buildProject } from "../../test/utils/project-fixture.util";
import { renderWithProject } from "../../test/utils/render-with-project.util";
import type { FailureResult } from "../../typing/types/failure.type";
import { FailureResultHistory } from "./failure-result-history";

const { columns, history } = englishFailures;

const buildResult = (overrides: Partial<FailureResult> = {}): FailureResult => {
  return {
    caseResultId: CASE_RESULT_ID,
    runId: RUN_ID,
    runStatus: "failed",
    runExecutor: "claude",
    status: "failed",
    durationMs: 65000,
    recordedAt: "2026-10-21T10:30:00Z",
    startedByName: "Quinn Qc",
    iteration: null,
    ...overrides,
  };
};

const readColumn = (columnName: string): string[] => {
  const table = within(screen.getByRole("region", { name: history.title })).getByRole("table");
  const headers = within(table).getAllByRole("columnheader");
  const columnIndex = headers.findIndex((header) => header.textContent === columnName);

  return within(table)
    .getAllByRole("row")
    .slice(1)
    .map((row) => within(row).getAllByRole("cell")[columnIndex]?.textContent ?? "");
};

describe("FailureResultHistory", () => {
  it("numbers each iteration of a data-driven case from 1", () => {
    renderWithProject(
      <FailureResultHistory
        results={[
          buildResult({ caseResultId: "d1000000-0000-4000-8000-000000000003", iteration: 2 }),
          buildResult({ caseResultId: "d1000000-0000-4000-8000-000000000002", iteration: 0 }),
          buildResult({ iteration: null, status: "passed" }),
        ]}
      />,
      buildProject(),
    );

    expect(screen.getByRole("columnheader", { name: columns.iteration })).toBeInTheDocument();
    expect(readColumn(columns.iteration)).toEqual(["3", "1", "—"]);
  });

  it("has no iteration column when no result is an iteration", () => {
    renderWithProject(<FailureResultHistory results={[buildResult()]} />, buildProject());

    expect(screen.getByRole("region", { name: history.title })).toBeInTheDocument();
    expect(screen.queryByRole("columnheader", { name: columns.iteration })).toBeNull();
  });
});
