import englishRuns from "@/lib/i18n/locales/en/runs.json";
import { routerReplace, setNavigation } from "@/modules/auth/test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "@/modules/auth/test/utils/api-result.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { RunsPage } from "./runs";
import { apiGet } from "./test/mocks/api-client.mock";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { PARENT_RUN_ID, RUN_ID, createRunSummary } from "./test/utils/run.fixture";
import { openSelectOption } from "./test/utils/select-option.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import type { RunFilters } from "./typing/types/run.type";
import { EMPTY_RUN_FILTERS } from "./utils/run-filters.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("@/modules/auth/test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface ListRequest {
  params: { query: Record<string, string | number> };
}

const RUNS_PATH = "/api/projects/{project_key}/runs";
const STORIES_PATH = "/api/projects/{project_key}/stories";
const PAGE_PATH = "/projects/APP/runs";
const ABORTED_RUN_ID = "a6000000-0000-4000-8000-000000000010";
const RERUN_ID = "a6000000-0000-4000-8000-000000000011";

const { abortReason, empty, filters, limitNotice, loadError, retry } = englishRuns;

const RUNS = [
  createRunSummary(),
  createRunSummary({
    id: ABORTED_RUN_ID,
    status: "aborted",
    abortReason: "inactive",
    executor: "manual",
    finishedAt: "2026-10-20T14:00:00Z",
  }),
  createRunSummary({
    id: RERUN_ID,
    status: "running",
    parentRunId: PARENT_RUN_ID,
    finishedAt: null,
    counts: { total: 1, passed: 0, failed: 0, blocked: 0, skipped: 0, notReported: 1 },
  }),
];

const STORIES = [
  { jiraKey: "APP-1", title: "Pay by card" },
  { jiraKey: "APP-2", title: "Refunds" },
];

const respond = (runs: ApiResult | (() => ApiResult)): void => {
  respondWithRoutes(apiGet, {
    [RUNS_PATH]: runs,
    [STORIES_PATH]: createSuccessResult(STORIES),
  });
};

const readListQueries = (): Record<string, string | number>[] => {
  return apiGet.mock.calls
    .filter(([path]) => path === RUNS_PATH)
    .map(([, options]) => (options as ListRequest).params.query);
};

const renderPage = (initialFilters: RunFilters = EMPTY_RUN_FILTERS) => {
  return renderWithProject(<RunsPage initialFilters={initialFilters} />);
};

const findRow = async (linkName: RegExp | string): Promise<HTMLElement> => {
  const links = await screen.findAllByRole("link", { name: linkName });

  return links[0].closest("tr") as HTMLElement;
};

describe("RunsPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    routerReplace.mockReset();
    setNavigation(PAGE_PATH);
    respond(createSuccessResult(RUNS));
  });

  it("lists every run with its story, status, executor, environment, starter, counts and duration", async () => {
    renderPage();

    const table = await screen.findByRole("table", { name: "Runs" });
    const firstRow = within(table).getAllByRole("row")[1];
    const row = within(firstRow);
    expect(row.getByRole("link", { name: /Oct/ })).toHaveAttribute(
      "href",
      `/projects/APP/runs/${RUN_ID}`,
    );
    expect(row.getByText("APP-1 · Pay by card")).toBeInTheDocument();
    expect(row.getByText("Failed")).toBeInTheDocument();
    expect(row.getByText("Claude")).toBeInTheDocument();
    expect(row.getByText("Staging")).toBeInTheDocument();
    expect(row.getByText("Alice Tester")).toBeInTheDocument();
    expect(row.getByText("3 passed · 1 failed · 2 not reported")).toBeInTheDocument();
    expect(row.getByText("6 cases")).toBeInTheDocument();
    expect(row.getByText("2m 5s")).toBeInTheDocument();
    expect(readListQueries()[0]).toEqual({ limit: 50 });
  });

  it("shows the abort reason of an aborted run", async () => {
    renderPage();

    await screen.findByRole("table", { name: "Runs" });
    const abortedRow = within(screen.getAllByRole("row")[2]);
    expect(abortedRow.getByText("Aborted")).toBeInTheDocument();
    expect(abortedRow.getByText(abortReason.inactive)).toBeInTheDocument();
    expect(abortedRow.getByText("Manual")).toBeInTheDocument();
  });

  it("links a re-run to its parent run and shows a running run in progress", async () => {
    renderPage();

    const parentLink = await screen.findByRole("link", { name: "Re-run of an earlier run" });
    expect(parentLink).toHaveAttribute("href", `/projects/APP/runs/${PARENT_RUN_ID}`);
    const rerunRow = within(parentLink.closest("tr") as HTMLElement);
    expect(rerunRow.getByText("Running")).toBeInTheDocument();
    expect(rerunRow.getByText("In progress")).toBeInTheDocument();
    expect(rerunRow.getByText("1 case")).toBeInTheDocument();
  });

  it("filters by status and story on the server and in the URL", async () => {
    const user = userEvent.setup();
    renderPage();
    await findRow(/Oct/);

    await user.click(screen.getByRole("radio", { name: "Failed" }));

    await waitFor(() => {
      expect(readListQueries()).toContainEqual({ status: "failed", limit: 50 });
    });
    expect(routerReplace).toHaveBeenLastCalledWith(`${PAGE_PATH}?status=failed`, {
      scroll: false,
    });

    await user.click(await openSelectOption(user, /^Story/, "APP-2 · Refunds"));

    await waitFor(() => {
      expect(readListQueries()).toContainEqual({
        status: "failed",
        storyKey: "APP-2",
        limit: 50,
      });
    });
    expect(routerReplace).toHaveBeenLastCalledWith(`${PAGE_PATH}?status=failed&story=APP-2`, {
      scroll: false,
    });
  });

  it("shows the empty state when the project has no runs", async () => {
    respond(createSuccessResult([]));
    const { container } = renderPage();

    expect(await screen.findByText(empty.title)).toBeInTheDocument();
    expect(screen.getByText(empty.description)).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the filtered empty state and clears the filters", async () => {
    const user = userEvent.setup();
    respond(createSuccessResult([]));
    renderPage({ status: "aborted", storyKey: "APP-1" });

    expect(await screen.findByText(empty.filteredTitle)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: filters.clear }));

    expect(routerReplace).toHaveBeenLastCalledWith(PAGE_PATH, { scroll: false });
    await waitFor(() => {
      expect(readListQueries()).toContainEqual({ limit: 50 });
    });
  });

  it("shows the filtered empty state for an unknown story key", async () => {
    respond(createErrorResult(404, "NOT_FOUND"));
    renderPage({ status: null, storyKey: "APP-404" });

    expect(await screen.findByText(empty.filteredTitle)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: filters.clear })).toBeInTheDocument();
    expect(screen.queryByText(loadError)).not.toBeInTheDocument();
  });

  it("shows an error with a retry", async () => {
    const user = userEvent.setup();
    let isFailing = true;
    respond(() => {
      return isFailing ? createErrorResult(500, "INVALID_REQUEST") : createSuccessResult(RUNS);
    });
    renderPage();

    expect(await screen.findByText(loadError)).toBeInTheDocument();
    isFailing = false;
    await user.click(screen.getByRole("button", { name: retry }));

    expect(await screen.findByRole("table", { name: "Runs" })).toBeInTheDocument();
  });

  it("explains the limit when the newest 50 runs are shown, and passes axe", async () => {
    const manyRuns = Array.from({ length: 50 }, (_, index) => {
      return createRunSummary({
        id: `a6000000-0000-4000-8000-${String(index).padStart(12, "0")}`,
      });
    });
    respond(createSuccessResult(manyRuns));
    const { container } = renderPage();

    expect(await screen.findByText(limitNotice.replace("{{count}}", "50"))).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });
});
