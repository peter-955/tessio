import englishSprints from "@/lib/i18n/locales/en/sprints.json";
import englishStories from "@/lib/i18n/locales/en/stories.json";
import englishTraceability from "@/lib/i18n/locales/en/traceability.json";
import type { Sprint } from "@/modules/sprints/typing/types/sprint.type";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { StoriesPage } from "./stories";
import { apiGet } from "./test/mocks/api-client.mock";
import { routerReplace, setNavigation } from "./test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "./test/utils/api-result.util";
import { buildProject } from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { openSelectOption } from "./test/utils/select-option.util";
import {
  ACTIVE_SPRINT_ID,
  buildStorySummary,
  buildSyncState,
  FUTURE_SPRINT_ID,
} from "./test/utils/story-fixture.util";
import {
  buildCoverage,
  buildStoryProgress,
  LAST_RUN_ID,
} from "./test/utils/story-progress-fixture.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import type { StoryFilters } from "./typing/types/story-filters.type";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface StoryListRequest {
  params: { query: Record<string, string> };
}

const STORIES_PATH = "/api/projects/{project_key}/stories";
const SPRINTS_PATH = "/api/projects/{project_key}/sprints";
const SYNC_PATH = "/api/projects/{project_key}/sync";
const PROGRESS_PATH = "/api/projects/{project_key}/story-progress";
const PAGE_PATH = "/projects/SHOP/stories";
const EMPTY_FILTERS: StoryFilters = { sprintId: null, testStatus: null, query: "" };

const { filters, list, empty, emptyFiltered, testStatuses } = englishStories;

const { storyColumns, runStatus } = englishTraceability;

const SPRINTS: Sprint[] = [
  {
    id: ACTIVE_SPRINT_ID,
    jiraSprintId: 12,
    name: "Sprint 12",
    state: "active",
    startAt: "2026-10-14T00:00:00Z",
    endAt: "2026-10-28T00:00:00Z",
    completeAt: null,
    storyCount: 2,
    syncedAt: "2026-10-20T09:00:00Z",
  },
  {
    id: FUTURE_SPRINT_ID,
    jiraSprintId: 13,
    name: "Sprint 13",
    state: "future",
    startAt: null,
    endAt: null,
    completeAt: null,
    storyCount: 0,
    syncedAt: "2026-10-20T09:00:00Z",
  },
];

const STORIES = [
  buildStorySummary(),
  buildStorySummary({
    id: "c1000000-0000-4000-8000-000000000002",
    jiraKey: "SHOP-2",
    jiraUrl: "https://shop.atlassian.net/browse/SHOP-2",
    title: "Refund an order",
    testStatus: "failed",
    sprintId: null,
    sprintName: null,
    criterionCount: 0,
    jiraMissingAt: "2026-10-18T09:00:00Z",
  }),
];

const PROGRESS = [
  buildStoryProgress(),
  buildStoryProgress({
    storyId: "c1000000-0000-4000-8000-000000000002",
    jiraKey: "SHOP-2",
    coverage: buildCoverage({
      criterionCount: 0,
      coveredCount: 0,
      passedCount: 0,
      failedCount: 0,
      uncoveredCount: 0,
    }),
    openGapCount: 0,
    activeFailureCount: 0,
    lastRun: null,
  }),
];

const readListQueries = (): Record<string, string>[] => {
  return apiGet.mock.calls
    .filter(([path]) => {
      return path === STORIES_PATH;
    })
    .map(([, options]) => {
      return (options as StoryListRequest).params.query;
    });
};

const readProgressQueries = (): Record<string, string>[] => {
  return apiGet.mock.calls
    .filter(([path]) => {
      return path === PROGRESS_PATH;
    })
    .map(([, options]) => {
      return (options as StoryListRequest).params.query;
    });
};

const respond = (
  stories: ApiResult | (() => ApiResult),
  progress: ApiResult = createSuccessResult(PROGRESS),
): void => {
  respondWithRoutes(apiGet, {
    [STORIES_PATH]: stories,
    [SPRINTS_PATH]: createSuccessResult(SPRINTS),
    [SYNC_PATH]: createSuccessResult(buildSyncState()),
    [PROGRESS_PATH]: progress,
  });
};

const renderPage = (initialFilters = EMPTY_FILTERS): ReturnType<typeof renderWithProject> => {
  return renderWithProject(<StoriesPage initialFilters={initialFilters} />, buildProject());
};

const chooseOption = async (user: UserEvent, label: string, option: string): Promise<void> => {
  await user.click(await openSelectOption(user, new RegExp(`^${label}`), option));
};

describe("StoriesPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    routerReplace.mockReset();
    setNavigation(PAGE_PATH);
    respond(createSuccessResult(STORIES));
  });

  it("lists stories with their status, sprint and Jira link", async () => {
    const { container } = renderPage();

    const keyLink = await screen.findByRole("link", { name: "SHOP-1" });
    expect(keyLink).toHaveAttribute("href", "/projects/SHOP/stories/SHOP-1");
    const firstRow = within(keyLink.closest("tr") as HTMLElement);
    expect(firstRow.getByText("Pay by card")).toBeInTheDocument();
    expect(firstRow.getByText("Sprint 12")).toBeInTheDocument();
    expect(firstRow.getByText("In Progress")).toBeInTheDocument();
    expect(firstRow.getByText(testStatuses.not_started)).toBeInTheDocument();
    expect(await firstRow.findByText("2/3")).toBeInTheDocument();
    const jiraLink = firstRow.getByRole("link", {
      name: new RegExp(`^${list.openInJira}\\s*SHOP-1$`),
    });
    expect(jiraLink).toHaveAttribute("href", "https://shop.atlassian.net/browse/SHOP-1");
    expect(jiraLink).toHaveAttribute("target", "_blank");
    expect(jiraLink).toHaveAttribute("rel", "noopener noreferrer");

    const secondRow = within(
      screen.getByRole("link", { name: "SHOP-2" }).closest("tr") as HTMLElement,
    );
    expect(secondRow.getByText(list.notInScope)).toBeInTheDocument();
    expect(secondRow.getByText(list.noSprint)).toBeInTheDocument();
    expect(secondRow.getByText(testStatuses.failed)).toBeInTheDocument();
    expect(readListQueries()[0]).toEqual({});
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the coverage, gaps, failures and last run of each story", async () => {
    renderPage();

    const keyLink = await screen.findByRole("link", { name: "SHOP-1" });
    expect(
      screen.getAllByRole("columnheader").map((header) => {
        return header.textContent;
      }),
    ).toEqual([
      englishStories.columns.key,
      englishStories.columns.title,
      englishStories.columns.sprint,
      englishStories.columns.jiraStatus,
      englishStories.columns.testStatus,
      storyColumns.coverage,
      storyColumns.openGaps,
      storyColumns.failures,
      storyColumns.lastRun,
      englishStories.columns.jira,
    ]);
    const firstRow = within(keyLink.closest("tr") as HTMLElement);
    expect(await firstRow.findByText("2/3")).toBeInTheDocument();
    expect(firstRow.getByText(storyColumns.failing.replace("{{count}}", "1"))).toBeInTheDocument();
    expect(firstRow.getByText("2")).toBeInTheDocument();
    expect(firstRow.getByText("1")).toBeInTheDocument();
    const runLink = firstRow.getByRole("link", { name: runStatus.failed });
    expect(runLink).toHaveAttribute("href", `/projects/SHOP/runs/${LAST_RUN_ID}`);

    const secondRow = within(
      screen.getByRole("link", { name: "SHOP-2" }).closest("tr") as HTMLElement,
    );
    expect(secondRow.getByText("—")).toBeInTheDocument();
    expect(secondRow.getAllByText("0")).toHaveLength(2);
    expect(secondRow.getByText(storyColumns.noRun)).toBeInTheDocument();
    expect(readProgressQueries()[0]).toEqual({});
  });

  it("asks for the progress of the chosen sprint", async () => {
    setNavigation(PAGE_PATH, `sprint=${ACTIVE_SPRINT_ID}`);
    renderPage({ ...EMPTY_FILTERS, sprintId: ACTIVE_SPRINT_ID });

    await screen.findByRole("link", { name: "SHOP-1" });
    expect(readProgressQueries()[0]).toEqual({ sprintId: ACTIVE_SPRINT_ID });
  });

  it("keeps the rows when the progress cannot be loaded", async () => {
    respond(createSuccessResult(STORIES), createErrorResult(500, "CONFLICT"));
    const { container } = renderPage();

    const keyLink = await screen.findByRole("link", { name: "SHOP-1" });
    const firstRow = within(keyLink.closest("tr") as HTMLElement);
    await waitFor(() => {
      expect(firstRow.getAllByText(storyColumns.unknown)).toHaveLength(4);
    });
    expect(firstRow.getByText("Pay by card")).toBeInTheDocument();
    expect(firstRow.queryByRole("link", { name: runStatus.failed })).toBeNull();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("sends the sprint and status filters and puts them in the URL", async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByRole("link", { name: "SHOP-1" });

    await chooseOption(user, filters.sprint, `Sprint 13 · ${englishSprints.states.future}`);
    await waitFor(() => {
      expect(readListQueries()).toContainEqual({ sprintId: FUTURE_SPRINT_ID });
    });
    expect(routerReplace).toHaveBeenLastCalledWith(`${PAGE_PATH}?sprint=${FUTURE_SPRINT_ID}`, {
      scroll: false,
    });

    await chooseOption(user, filters.status, testStatuses.passed);
    await waitFor(() => {
      expect(readListQueries()).toContainEqual({
        sprintId: FUTURE_SPRINT_ID,
        testStatus: "passed",
      });
    });
    expect(routerReplace).toHaveBeenLastCalledWith(
      `${PAGE_PATH}?sprint=${FUTURE_SPRINT_ID}&status=passed`,
      { scroll: false },
    );

    await chooseOption(user, filters.sprint, filters.allSprints);
    expect(routerReplace).toHaveBeenLastCalledWith(`${PAGE_PATH}?status=passed`, {
      scroll: false,
    });
  });

  it("debounces the search before querying", async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByRole("link", { name: "SHOP-1" });

    await user.type(screen.getByRole("textbox", { name: filters.search }), " refund");

    await waitFor(() => {
      expect(readListQueries()).toContainEqual({ query: "refund" });
    });
    const searchedQueries = readListQueries().filter((query) => {
      return query.query !== undefined;
    });
    expect(searchedQueries).toEqual([{ query: "refund" }]);
    expect(routerReplace).toHaveBeenCalledTimes(1);
    expect(routerReplace).toHaveBeenLastCalledWith(`${PAGE_PATH}?query=refund`, {
      scroll: false,
    });
  });

  it("follows the URL when it changes without a remount", async () => {
    setNavigation(PAGE_PATH, "status=passed&query=pay");
    const filtered = { ...EMPTY_FILTERS, testStatus: "passed" as const, query: "pay" };
    const { rerenderWithProject } = renderPage(filtered);
    await screen.findByRole("link", { name: "SHOP-1" });
    expect(screen.getByRole("textbox", { name: filters.search })).toHaveValue("pay");

    setNavigation(PAGE_PATH);
    rerenderWithProject(<StoriesPage initialFilters={filtered} />);

    await waitFor(() => {
      expect(screen.getByRole("textbox", { name: filters.search })).toHaveValue("");
    });
    expect(screen.getByRole("combobox", { name: filters.status })).toHaveValue(filters.allStatuses);
    await waitFor(() => {
      expect(readListQueries().at(-1)).toEqual({});
    });
    expect(routerReplace).not.toHaveBeenCalled();
  });

  it("starts from the filters in the URL", async () => {
    setNavigation(PAGE_PATH, `sprint=${ACTIVE_SPRINT_ID}&status=failed&query=pay`);
    renderPage({ sprintId: ACTIVE_SPRINT_ID, testStatus: "failed", query: "pay" });

    await screen.findByRole("link", { name: "SHOP-1" });
    expect(readListQueries()[0]).toEqual({
      sprintId: ACTIVE_SPRINT_ID,
      testStatus: "failed",
      query: "pay",
    });
    expect(screen.getByRole("textbox", { name: filters.search })).toHaveValue("pay");
  });

  it("shows the empty state without filters", async () => {
    respond(createSuccessResult([]));
    renderPage();

    expect(await screen.findByText(empty.title)).toBeInTheDocument();
    expect(screen.getByText(empty.description)).toBeInTheDocument();
  });

  it("shows the filtered empty state with filters", async () => {
    respond(createSuccessResult([]));
    renderPage({ ...EMPTY_FILTERS, testStatus: "passed" });

    expect(await screen.findByText(emptyFiltered.title)).toBeInTheDocument();
    expect(screen.queryByText(empty.title)).toBeNull();
  });

  it("shows a loading state", () => {
    respond(() => {
      return createSuccessResult(STORIES);
    });
    apiGet.mockImplementation(() => {
      return new Promise(() => {
        return;
      });
    });
    const { container } = renderPage();

    expect(container.querySelector('[aria-busy="true"]')).not.toBeNull();
  });

  it("shows an error and retries", async () => {
    const user = userEvent.setup();
    let isFailing = true;
    respond(() => {
      return isFailing ? createErrorResult(500, "CONFLICT") : createSuccessResult(STORIES);
    });
    renderPage();

    expect(await screen.findByText(englishStories.loadError)).toBeInTheDocument();
    isFailing = false;
    await user.click(screen.getByRole("button", { name: englishStories.retry }));

    expect(await screen.findByRole("link", { name: "SHOP-1" })).toBeInTheDocument();
  });

  it("hides the sprint filter when sprints cannot be loaded", async () => {
    respondWithRoutes(apiGet, {
      [STORIES_PATH]: createSuccessResult(STORIES),
      [SPRINTS_PATH]: createErrorResult(500, "CONFLICT"),
      [SYNC_PATH]: createSuccessResult(buildSyncState()),
      [PROGRESS_PATH]: createSuccessResult(PROGRESS),
    });
    renderPage();

    await screen.findByRole("link", { name: "SHOP-1" });
    await waitFor(() => {
      expect(screen.queryByRole("combobox", { name: filters.sprint })).toBeNull();
    });
    expect(screen.getByRole("combobox", { name: filters.status })).toBeInTheDocument();
  });
});
