import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen, within } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { DSTraceabilityMatrix } from "./traceability-matrix";
import type {
  DSTraceabilityCase,
  DSTraceabilityCriterion,
  DSTraceabilityMatrixLabels,
} from "./traceability-matrix.type";

const LABELS: DSTraceabilityMatrixLabels = {
  caption: "Acceptance criteria by test case for SHOP-1",
  criterion: "Acceptance criterion",
  status: "AC status",
  notLinked: "Not linked",
  resultStatuses: {
    passed: "Passed",
    failed: "Failed",
    blocked: "Blocked",
    skipped: "Skipped",
    not_run: "Not run",
  },
  criterionStatuses: {
    uncovered: "Uncovered",
    not_run: "Not run",
    passed: "Passed",
    failed: "Failed",
    blocked: "Blocked",
  },
};

const CASES: DSTraceabilityCase[] = [
  {
    id: "case-1",
    code: "TC-1",
    title: "Pay with a valid card",
    href: "/projects/SHOP/test-cases/TC-1",
    resultStatus: "failed",
    markers: [],
  },
  {
    id: "case-2",
    code: "TC-2",
    title: "Decline an expired card",
    href: "/projects/SHOP/test-cases/TC-2",
    resultStatus: "not_run",
    markers: ["Draft", "Needs review"],
  },
];

const CRITERIA: DSTraceabilityCriterion[] = [
  {
    id: "criterion-1",
    code: "AC1",
    text: "Card payment succeeds",
    status: "failed",
    removedLabel: null,
    linkedCaseIds: ["case-1"],
  },
  {
    id: "criterion-2",
    code: "AC2",
    text: "Declined card shows an error",
    status: "uncovered",
    removedLabel: null,
    linkedCaseIds: [],
  },
  {
    id: "criterion-3",
    code: "AC3",
    text: "Old rule",
    status: "not_run",
    removedLabel: "Removed from Jira on Oct 18, 2026",
    linkedCaseIds: ["case-2"],
  },
];

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

const renderMatrix = (): ReturnType<typeof render> => {
  return render(<DSTraceabilityMatrix criteria={CRITERIA} cases={CASES} labels={LABELS} />, {
    wrapper,
  });
};

const findRow = (code: string): HTMLElement => {
  return screen
    .getByRole("rowheader", { name: new RegExp(`^${code}`) })
    .closest("tr") as HTMLElement;
};

describe("DSTraceabilityMatrix", () => {
  it("renders the column and row headers", () => {
    renderMatrix();

    expect(screen.getByRole("table", { name: LABELS.caption })).toBeInTheDocument();
    const headers = screen.getAllByRole("columnheader");
    expect(headers.map((header) => header.textContent)).toEqual([
      "Acceptance criterion",
      "AC status",
      "TC-1Pay with a valid card",
      "TC-2Decline an expired cardDraftNeeds review",
    ]);
    const caseLink = within(headers[2] as HTMLElement).getByRole("link", { name: "TC-1" });
    expect(caseLink).toHaveAttribute("href", "/projects/SHOP/test-cases/TC-1");
    expect(caseLink).toHaveAttribute("title", "Pay with a valid card");
    expect(screen.getAllByRole("rowheader").map((header) => header.textContent)).toEqual([
      "AC1Card payment succeeds",
      "AC2Declined card shows an error",
      "AC3Old ruleRemoved from Jira on Oct 18, 2026",
    ]);
  });

  it("shows the result label in a linked cell and a hidden label in an unlinked one", () => {
    renderMatrix();

    const cells = within(findRow("AC1")).getAllByRole("cell");
    expect(cells.map((cell) => cell.textContent)).toEqual(["Failed", "Failed", "·Not linked"]);
    expect(within(cells[2] as HTMLElement).getByText("·")).toHaveAttribute("aria-hidden", "true");
    expect(within(findRow("AC2")).getAllByRole("cell")[0]).toHaveTextContent("Uncovered");
  });

  it("strikes through a removed criterion and shows its label", () => {
    renderMatrix();

    const row = findRow("AC3");
    expect(within(row).getByText("Old rule").tagName).toBe("S");
    expect(within(row).getByText("Removed from Jira on Oct 18, 2026")).toBeInTheDocument();
    expect(within(row).getAllByRole("cell")[2]).toHaveTextContent("Not run");
  });

  it("has no accessibility violations", async () => {
    const { container } = renderMatrix();

    expect(await axe(container)).toHaveNoViolations();
  });
});
