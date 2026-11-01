import { describe, expect, it } from "vitest";
import {
  buildCriterionTrace,
  buildTracedCase,
  REMOVED_CRITERION_ID,
  THIRD_CRITERION_ID,
  TRACED_CASES,
  TRACED_CRITERIA,
} from "../test/utils/traceability-fixture.util";
import type { MatrixCaseLabels } from "../typing/types/matrix-case-labels.type";
import { buildMatrixCases, buildMatrixCriteria, listUncoveredCriteria } from "./matrix.util";

const LABELS: MatrixCaseLabels = {
  notReady: { draft: "Draft", in_review: "In review" },
  needsReview: "Needs review",
};

describe("buildMatrixCases", () => {
  it("links each case and uses its latest result or not run", () => {
    expect(buildMatrixCases(TRACED_CASES, "SHOP", LABELS)).toEqual([
      {
        id: TRACED_CASES[0]?.id,
        code: "TC-1",
        title: "Pay with a valid card",
        href: "/projects/SHOP/test-cases/TC-1",
        resultStatus: "failed",
        markers: [],
      },
      {
        id: TRACED_CASES[1]?.id,
        code: "TC-2",
        title: "Decline an expired card",
        href: "/projects/SHOP/test-cases/TC-2",
        resultStatus: "not_run",
        markers: ["Draft", "Needs review"],
      },
    ]);
  });

  it("marks a case in review", () => {
    const [matrixCase] = buildMatrixCases(
      [buildTracedCase({ status: "in_review" })],
      "SHOP",
      LABELS,
    );

    expect(matrixCase?.markers).toEqual(["In review"]);
  });
});

describe("buildMatrixCriteria", () => {
  it("formats the removal date and keeps the linked cases", () => {
    const criteria = buildMatrixCriteria(TRACED_CRITERIA, (removedAt) => {
      return `Removed ${removedAt}`;
    });

    expect(criteria[0]).toEqual({
      id: TRACED_CRITERIA[0]?.id,
      code: "AC1",
      text: "Card payment succeeds",
      status: "failed",
      removedLabel: null,
      linkedCaseIds: TRACED_CRITERIA[0]?.linkedCaseIds,
    });
    expect(criteria[3]?.removedLabel).toBe("Removed 2026-10-18T09:00:00Z");
  });
});

describe("listUncoveredCriteria", () => {
  it("returns only the active uncovered criteria", () => {
    expect(
      listUncoveredCriteria(TRACED_CRITERIA).map((criterion) => {
        return criterion.id;
      }),
    ).toEqual([THIRD_CRITERION_ID]);
    expect(
      listUncoveredCriteria([
        buildCriterionTrace({ id: REMOVED_CRITERION_ID, removedAt: "2026-10-18T09:00:00Z" }),
      ]),
    ).toEqual([]);
  });
});
