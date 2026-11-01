import englishTraceability from "@/lib/i18n/locales/en/traceability.json";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { StoryTraceability } from "./story-traceability";
import { apiGet } from "./test/mocks/api-client.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "./test/utils/api-result.util";
import { interpolate } from "./test/utils/interpolate.util";
import { buildProject, QC_CAPABILITIES } from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import {
  buildCoverageCount,
  buildCriterionTrace,
  buildTraceability,
  TRACED_CRITERIA,
} from "./test/utils/traceability-fixture.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

interface TraceabilityRequest {
  params: { path: Record<string, string> };
}

const TRACEABILITY_PATH = "/api/projects/{project_key}/stories/{jira_key}/traceability";

const { matrix, resultStatus, criterionStatus, uncovered, empty, coverage } = englishTraceability;

const respond = (traceability: ApiResult | (() => ApiResult)): void => {
  respondWithRoutes(apiGet, { [TRACEABILITY_PATH]: traceability });
};

const renderTab = (capabilities = QC_CAPABILITIES, isArchived = false) => {
  return renderWithProject(
    <StoryTraceability jiraKey="SHOP-1" />,
    buildProject({ capabilities, isArchived }),
  );
};

const findBanner = async (title: string): Promise<HTMLElement> => {
  return (await screen.findByText(title)).closest('[role="alert"]') as HTMLElement;
};

const findRow = (code: string): HTMLElement => {
  return screen
    .getByRole("rowheader", { name: new RegExp(`^${code}`) })
    .closest("tr") as HTMLElement;
};

describe("StoryTraceability", () => {
  beforeEach(() => {
    apiGet.mockReset();
    respond(createSuccessResult(buildTraceability()));
  });

  it("shows every criterion by case with the latest results", async () => {
    const { container } = renderTab();

    expect(
      await screen.findByRole("table", {
        name: interpolate(matrix.caption, { jiraKey: "SHOP-1" }),
      }),
    ).toBeInTheDocument();
    expect((apiGet.mock.calls[0]?.[1] as TraceabilityRequest).params.path).toEqual({
      project_key: "SHOP",
      jira_key: "SHOP-1",
    });
    expect(screen.getByRole("heading", { name: englishTraceability.title })).toBeInTheDocument();
    expect(
      screen.getByText(interpolate(coverage.covered, { covered: "2", total: "3" })),
    ).toBeInTheDocument();
    expect(screen.getByText(interpolate(coverage.failed, { count: "1" }))).toBeInTheDocument();
    expect(screen.getByText(interpolate(coverage.notRun, { count: "1" }))).toBeInTheDocument();
    expect(screen.queryByText(interpolate(coverage.passed, { count: "0" }))).toBeNull();

    expect(screen.getAllByRole("columnheader").map((header) => header.textContent)).toEqual([
      matrix.criterion,
      matrix.status,
      "TC-1Pay with a valid card",
      `TC-2Decline an expired card${matrix.notReady.draft}${matrix.needsReview}`,
    ]);
    expect(screen.getByRole("link", { name: "TC-1" })).toHaveAttribute(
      "href",
      "/projects/SHOP/test-cases/TC-1",
    );
    expect(screen.getAllByRole("rowheader")).toHaveLength(4);
    expect(
      within(findRow("AC1"))
        .getAllByRole("cell")
        .map((cell) => cell.textContent),
    ).toEqual([criterionStatus.failed, resultStatus.failed, `·${matrix.notLinked}`]);
    expect(
      within(findRow("AC2"))
        .getAllByRole("cell")
        .map((cell) => cell.textContent),
    ).toEqual([criterionStatus.not_run, `·${matrix.notLinked}`, resultStatus.not_run]);
    expect(within(findRow("AC3")).getAllByRole("cell")[0]).toHaveTextContent(
      criterionStatus.uncovered,
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows a skeleton while loading", () => {
    apiGet.mockImplementation(() => {
      return new Promise(() => {
        return;
      });
    });
    const { container } = renderTab();

    expect(container.querySelector('[aria-busy="true"]')).not.toBeNull();
  });

  it("shows an error and retries", async () => {
    const user = userEvent.setup();
    let isFailing = true;
    respond(() => {
      return isFailing
        ? createErrorResult(500, "CONFLICT")
        : createSuccessResult(buildTraceability());
    });
    renderTab();

    expect(await screen.findByText(englishTraceability.loadError)).toBeInTheDocument();
    isFailing = false;
    await user.click(screen.getByRole("button", { name: englishTraceability.retry }));

    expect(await screen.findByRole("rowheader", { name: /^AC1/ })).toBeInTheDocument();
  });

  it("warns about one uncovered criterion and offers a new test case", async () => {
    renderTab();

    const banner = await findBanner(interpolate(uncovered.title_one, { count: "1" }));
    expect(
      within(banner).getByText(interpolate(uncovered.description, { codes: "AC3" })),
    ).toBeInTheDocument();
    expect(within(banner).getByRole("link", { name: uncovered.action })).toHaveAttribute(
      "href",
      "/projects/SHOP/test-cases/new?story=SHOP-1",
    );
  });

  it("uses the plural and lists every uncovered code", async () => {
    respond(
      createSuccessResult(
        buildTraceability({
          criteria: [
            buildCriterionTrace({ status: "uncovered", linkedCaseIds: [] }),
            ...TRACED_CRITERIA.slice(1),
          ],
        }),
      ),
    );
    renderTab();

    const banner = await findBanner(interpolate(uncovered.title_other, { count: "2" }));
    expect(
      within(banner).getByText(interpolate(uncovered.description, { codes: "AC1, AC3" })),
    ).toBeInTheDocument();
  });

  it("strikes through a removed criterion and leaves it out of the banner", async () => {
    renderTab();

    const banner = await findBanner(interpolate(uncovered.title_one, { count: "1" }));
    expect(within(banner).queryByText(/AC4/)).toBeNull();
    const removedRow = findRow("AC4");
    expect(within(removedRow).getByText("Old rule").tagName).toBe("S");
    expect(
      within(removedRow).getByText(interpolate(matrix.removed, { date: "Oct 18, 2026" })),
    ).toBeInTheDocument();
    expect(screen.getAllByRole("rowheader").at(-1)).toBe(within(removedRow).getByRole("rowheader"));
  });

  it("shows no banner when every active criterion is covered", async () => {
    respond(
      createSuccessResult(
        buildTraceability({
          coverage: buildCoverageCount({ uncoveredCount: 0 }),
          criteria: [TRACED_CRITERIA[0], TRACED_CRITERIA[1], TRACED_CRITERIA[3]].flatMap(
            (criterion) => {
              return criterion === undefined ? [] : [criterion];
            },
          ),
        }),
      ),
    );
    renderTab();

    await screen.findByRole("rowheader", { name: /^AC1/ });
    expect(screen.queryByText(new RegExp(uncovered.action))).toBeNull();
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("hides New test case from a viewer and on an archived project", async () => {
    const { unmount } = renderTab(buildProject().capabilities);

    expect(await findBanner(interpolate(uncovered.title_one, { count: "1" }))).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: uncovered.action })).toBeNull();
    unmount();

    renderTab(QC_CAPABILITIES, true);
    expect(await findBanner(interpolate(uncovered.title_one, { count: "1" }))).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: uncovered.action })).toBeNull();
  });

  it("shows the no criteria state", async () => {
    respond(createSuccessResult(buildTraceability({ criteria: [], cases: [] })));
    const { container } = renderTab();

    expect(await screen.findByText(empty.noCriteria.title)).toBeInTheDocument();
    expect(screen.getByText(empty.noCriteria.description)).toBeInTheDocument();
    expect(screen.queryByRole("table")).toBeNull();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the no cases state with New test case for an editor", async () => {
    respond(
      createSuccessResult(
        buildTraceability({
          coverage: buildCoverageCount({
            coveredCount: 0,
            failedCount: 0,
            notRunCount: 0,
            uncoveredCount: 3,
          }),
          criteria: TRACED_CRITERIA.map((criterion) => {
            return { ...criterion, status: "uncovered", linkedCaseIds: [] };
          }),
          cases: [],
        }),
      ),
    );
    renderTab();

    expect(await screen.findByText(empty.noCases.title)).toBeInTheDocument();
    expect(screen.getByText(empty.noCases.description)).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: uncovered.action })).toHaveLength(2);
    expect(screen.queryByRole("table")).toBeNull();
  });

  it("shows the no cases state without New test case for a viewer", async () => {
    respond(createSuccessResult(buildTraceability({ cases: [] })));
    renderTab(buildProject().capabilities);

    expect(await screen.findByText(empty.noCases.title)).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: uncovered.action })).toBeNull();
  });
});
