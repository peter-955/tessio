import englishDashboard from "@/lib/i18n/locales/en/dashboard.json";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet } from "../../test/mocks/api-client.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "../../test/utils/api-result.util";
import {
  buildDraftCase,
  buildFailureToFix,
  buildGapToAnswer,
  buildMyWork,
  buildUncoveredCriterion,
  FAILURE_ID,
} from "../../test/utils/my-work-fixture.util";
import { buildProject } from "../../test/utils/project-fixture.util";
import { renderWithProject } from "../../test/utils/render-with-project.util";
import type { MyWork } from "../../typing/types/my-work.type";
import { MyWorkPanel } from "./my-work-panel";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("../../test/mocks/next-navigation.mock")).nextNavigationMock;
});

const MY_WORK_PATH = "/api/projects/{project_key}/my-work";

const { myWork } = englishDashboard;

const respond = (result: ApiResult | (() => ApiResult)): void => {
  respondWithRoutes(apiGet, { [MY_WORK_PATH]: result });
};

const renderPanel = (work: MyWork): ReturnType<typeof renderWithProject> => {
  respond(createSuccessResult(work));

  return renderWithProject(<MyWorkPanel projectKey="SHOP" sprintId={null} />, buildProject());
};

const readSectionTitles = (): string[] => {
  return screen.getAllByRole("heading", { level: 3 }).map((heading) => {
    return heading.textContent ?? "";
  });
};

const findSection = (title: string): HTMLElement => {
  return screen.getByRole("heading", { name: title }).closest("section") as HTMLElement;
};

describe("MyWorkPanel", () => {
  beforeEach(() => {
    apiGet.mockReset();
  });

  it("shows the uncovered criteria and draft cases for QC", async () => {
    const { container } = renderPanel(
      buildMyWork({ role: "qc", sections: ["cases_to_write", "gaps_to_answer"] }),
    );

    expect(await screen.findByText(`As ${myWork.roles.qc}`)).toBeInTheDocument();
    expect(readSectionTitles()).toEqual([
      myWork.uncovered.title,
      myWork.drafts.title,
      myWork.gaps.title,
    ]);

    const uncovered = within(findSection(myWork.uncovered.title));
    expect(uncovered.getByText("AC-1")).toBeInTheDocument();
    expect(uncovered.getByText("The card is charged once")).toBeInTheDocument();
    expect(uncovered.getByRole("link", { name: "SHOP-1" })).toHaveAttribute(
      "href",
      "/projects/SHOP/stories/SHOP-1",
    );
    expect(uncovered.getByRole("link", { name: myWork.uncovered.write })).toHaveAttribute(
      "href",
      "/projects/SHOP/test-cases/new?story=SHOP-1",
    );

    const drafts = within(findSection(myWork.drafts.title));
    expect(drafts.getByRole("link", { name: "Refund a card payment" })).toHaveAttribute(
      "href",
      "/projects/SHOP/test-cases/TC-7",
    );
    expect(drafts.getByText(englishDashboard.statuses.case.draft)).toBeInTheDocument();
    expect(drafts.getByText("SHOP-2")).toBeInTheDocument();

    const gaps = within(findSection(myWork.gaps.title));
    expect(gaps.getByRole("link", { name: "Which currencies are allowed?" })).toHaveAttribute(
      "href",
      "/projects/SHOP/stories/SHOP-4?tab=gaps",
    );
    expect(gaps.getByText(englishDashboard.statuses.severity.high)).toBeInTheDocument();
    expect(gaps.getByText(englishDashboard.statuses.gapType.missing_ac)).toBeInTheDocument();
    expect(gaps.getByRole("link", { name: myWork.viewAll })).toHaveAttribute("href", "/gaps");
    expect(screen.queryByText(myWork.failures.title)).toBeNull();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the failures to fix for a developer", async () => {
    renderPanel(buildMyWork({ role: "dev", sections: ["failures_to_fix", "gaps_to_answer"] }));

    expect(await screen.findByText(`As ${myWork.roles.dev}`)).toBeInTheDocument();
    expect(readSectionTitles()).toEqual([myWork.failures.title, myWork.gaps.title]);

    const failures = within(findSection(myWork.failures.title));
    expect(failures.getByRole("link", { name: "Checkout with an expired card" })).toHaveAttribute(
      "href",
      `/projects/SHOP/failures/${FAILURE_ID}`,
    );
    expect(failures.getByText("TC-3")).toBeInTheDocument();
    expect(failures.getByText(englishDashboard.statuses.failure.open)).toBeInTheDocument();
    expect(failures.getByText("Opened Oct 20, 09:00 AM UTC")).toBeInTheDocument();
    expect(failures.getByRole("link", { name: myWork.viewAll })).toHaveAttribute(
      "href",
      "/projects/SHOP/failures",
    );
    expect(screen.queryByText(myWork.uncovered.title)).toBeNull();
  });

  it("tells a viewer that nothing is assigned to the role", async () => {
    const { container } = renderPanel(buildMyWork({ role: "viewer", sections: [] }));

    expect(await screen.findByText(myWork.nothingForRole)).toBeInTheDocument();
    expect(screen.queryAllByRole("heading", { level: 3 })).toHaveLength(0);
    expect(screen.getByRole("link", { name: "2 unassigned failures" })).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("says how many items are shown when the list is cut", async () => {
    const items = Array.from({ length: 20 }, (_, index) => {
      return buildFailureToFix({
        failureId: `f1000000-0000-4000-8000-${String(index).padStart(12, "0")}`,
        caseCode: `TC-${index + 1}`,
        caseTitle: `Failure ${index + 1}`,
      });
    });
    renderPanel(
      buildMyWork({
        role: "dev",
        sections: ["failures_to_fix"],
        failuresToFix: { totalCount: 25, items },
      }),
    );

    const failures = within(
      (await screen.findByRole("heading", { name: myWork.failures.title })).closest(
        "section",
      ) as HTMLElement,
    );
    expect(failures.getAllByRole("listitem")).toHaveLength(20);
    expect(failures.getByText("Showing 20 of 25")).toBeInTheDocument();
  });

  it("shows the empty label of an empty list", async () => {
    renderPanel(
      buildMyWork({
        role: "qc",
        sections: ["cases_to_write"],
        uncoveredCriteria: { totalCount: 0, items: [] },
        draftCases: { totalCount: 2, items: [buildDraftCase(), buildDraftCase({ caseId: "b2" })] },
      }),
    );

    expect(await screen.findByText(myWork.uncovered.empty)).toBeInTheDocument();
    expect(screen.queryByText(/^Showing/)).toBeNull();
  });

  it("links the unassigned failure count to the filtered failure list", async () => {
    renderPanel(buildMyWork({ unassignedFailureCount: 3 }));

    expect(await screen.findByRole("link", { name: "3 unassigned failures" })).toHaveAttribute(
      "href",
      "/projects/SHOP/failures?assignee=unassigned",
    );
  });

  it("shows the no-unassigned text without a link when the count is zero", async () => {
    renderPanel(buildMyWork({ unassignedFailureCount: 0 }));

    expect(await screen.findByText(myWork.noUnassigned)).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /unassigned failures/ })).toBeNull();
  });

  it("shows an error and retries", async () => {
    const user = userEvent.setup();
    let isFailing = true;
    respond(() => {
      return isFailing
        ? createErrorResult(500, "CONFLICT")
        : createSuccessResult(
            buildMyWork({
              uncoveredCriteria: { totalCount: 1, items: [buildUncoveredCriterion()] },
              gapsToAnswer: { totalCount: 1, items: [buildGapToAnswer()] },
            }),
          );
    });
    renderWithProject(<MyWorkPanel projectKey="SHOP" sprintId={null} />, buildProject());

    expect(await screen.findByText(myWork.loadError)).toBeInTheDocument();
    isFailing = false;
    await user.click(screen.getByRole("button", { name: englishDashboard.retry }));

    expect(await screen.findByText(`As ${myWork.roles.admin}`)).toBeInTheDocument();
  });

  it("renders nothing when the sprint is not found", async () => {
    respond(createErrorResult(404, "NOT_FOUND"));
    const { container } = renderWithProject(
      <MyWorkPanel projectKey="SHOP" sprintId="9d9d9d9d-9d9d-4d9d-8d9d-9d9d9d9d9d9d" />,
      buildProject(),
    );

    await vi.waitFor(() => {
      expect(apiGet).toHaveBeenCalled();
    });
    await vi.waitFor(() => {
      expect(screen.queryByText(myWork.title)).toBeNull();
    });
    expect(container.querySelector("[aria-busy]")).toBeNull();
  });
});
