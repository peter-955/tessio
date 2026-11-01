import englishFailures from "@/lib/i18n/locales/en/failures.json";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { FailuresPage } from "./failures";
import { apiGet } from "./test/mocks/api-client.mock";
import { routerReplace, setNavigation } from "./test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "./test/utils/api-result.util";
import {
  DEACTIVATED_USER_ID,
  MEMBERS,
  buildFailure,
  buildStorySummary,
} from "./test/utils/failure-fixture.util";
import { buildProject } from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { openSelectOption } from "./test/utils/select-option.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import type { FailureFilters } from "./typing/types/failure-filters.type";
import { EMPTY_FAILURE_FILTERS, parseFailureFilters } from "./utils/failure-filters.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

vi.mock("@/components/session-guard/hooks/use-current-user", async () => {
  return (await import("./test/mocks/current-user.mock")).currentUserMock;
});

interface ListRequest {
  params: { query: Record<string, unknown> };
}

const FAILURES_PATH = "/api/projects/{project_key}/failures";
const MEMBERS_PATH = "/api/projects/{project_key}/members";
const STORIES_PATH = "/api/projects/{project_key}/stories";
const PAGE_PATH = "/projects/SHOP/failures";

const { columns, empty, filters, status, assignee } = englishFailures;

const FAILURES = [
  buildFailure(),
  buildFailure({
    id: "f1000000-0000-4000-8000-000000000002",
    testCaseCode: "TC-2",
    testCaseTitle: "Refund an order",
    storyJiraKey: "SHOP-2",
    status: "fixed",
    assigneeId: DEACTIVATED_USER_ID,
    assigneeName: "Ann Old",
    assigneeStatus: "deactivated",
  }),
];

const respond = (failures: ApiResult | (() => ApiResult)): void => {
  respondWithRoutes(apiGet, {
    [FAILURES_PATH]: failures,
    [MEMBERS_PATH]: createSuccessResult(MEMBERS),
    [STORIES_PATH]: createSuccessResult([
      buildStorySummary(),
      buildStorySummary({
        id: "c1000000-0000-4000-8000-000000000002",
        jiraKey: "SHOP-2",
        title: "Refunds",
      }),
    ]),
  });
};

const readListQueries = (): Record<string, unknown>[] => {
  return apiGet.mock.calls
    .filter(([path]) => {
      return path === FAILURES_PATH;
    })
    .map(([, options]) => {
      return (options as ListRequest).params.query;
    });
};

const renderPage = (
  initialFilters: FailureFilters = EMPTY_FAILURE_FILTERS,
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(<FailuresPage initialFilters={initialFilters} />, buildProject());
};

const chooseOption = async (user: UserEvent, label: string, option: string): Promise<void> => {
  await user.click(await openSelectOption(user, new RegExp(`^${label}`), option));
};

describe("FailuresPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    routerReplace.mockReset();
    setNavigation(PAGE_PATH);
    respond(createSuccessResult(FAILURES));
  });

  it("lists the failures with their story, status and assignee", async () => {
    const { container } = renderPage();

    const caseLink = await screen.findByRole("link", { name: "TC-1 · Pay with a valid card" });
    expect(caseLink).toHaveAttribute(
      "href",
      "/projects/SHOP/failures/f1000000-0000-4000-8000-000000000001",
    );
    const firstRow = within(caseLink.closest("tr") as HTMLElement);
    expect(firstRow.getByRole("link", { name: "SHOP-1" })).toHaveAttribute(
      "href",
      "/projects/SHOP/stories/SHOP-1",
    );
    expect(firstRow.getByText(status.open)).toBeInTheDocument();
    expect(firstRow.getByText(assignee.unassigned)).toBeInTheDocument();
    expect(firstRow.getByRole("link", { name: /Oct 21/ }).getAttribute("href")).toBe(
      "/projects/SHOP/runs/b1000000-0000-4000-8000-000000000001",
    );

    const secondRow = within(
      screen.getByRole("link", { name: "TC-2 · Refund an order" }).closest("tr") as HTMLElement,
    );
    expect(secondRow.getByText(status.fixed)).toBeInTheDocument();
    expect(secondRow.getByText("Ann Old")).toBeInTheDocument();
    expect(secondRow.getByText(assignee.deactivated)).toBeInTheDocument();
    expect(screen.getAllByRole("columnheader").map((header) => header.textContent)).toEqual([
      columns.testCase,
      columns.story,
      columns.status,
      columns.assignee,
      columns.lastFailed,
    ]);
    expect(readListQueries()[0]).toEqual({ status: ["open", "fixed", "reopened"] });
    expect(await axe(container)).toHaveNoViolations();
  });

  it("filters unassigned failures and puts the filter in the URL", async () => {
    const user = userEvent.setup();
    renderPage();

    await screen.findByRole("link", { name: "TC-1 · Pay with a valid card" });
    await chooseOption(user, filters.assignee, filters.unassigned);

    await waitFor(() => {
      expect(readListQueries().at(-1)).toEqual({
        status: ["open", "fixed", "reopened"],
        unassigned: true,
      });
    });
    expect(routerReplace).toHaveBeenLastCalledWith(`${PAGE_PATH}?assignee=unassigned`, {
      scroll: false,
    });
  });

  it("sends the current user for Assigned to me", async () => {
    const user = userEvent.setup();
    renderPage();

    await screen.findByRole("link", { name: "TC-1 · Pay with a valid card" });
    await chooseOption(user, filters.assignee, filters.me);

    await waitFor(() => {
      expect(readListQueries().at(-1)).toEqual({
        status: ["open", "fixed", "reopened"],
        assigneeId: "a1000000-0000-4000-8000-000000000001",
      });
    });
    expect(routerReplace).toHaveBeenLastCalledWith(`${PAGE_PATH}?assignee=me`, { scroll: false });
  });

  it("drops the status from the query for All statuses", async () => {
    const user = userEvent.setup();
    renderPage();

    await screen.findByRole("link", { name: "TC-1 · Pay with a valid card" });
    await chooseOption(user, filters.status, filters.all);

    await waitFor(() => {
      expect(readListQueries().at(-1)).toEqual({});
    });
    expect(routerReplace).toHaveBeenLastCalledWith(`${PAGE_PATH}?status=all`, { scroll: false });
  });

  it("sends the story of the initial URL", async () => {
    setNavigation(PAGE_PATH, "story=TES-1");
    renderPage(parseFailureFilters({ story: "TES-1" }));

    await screen.findByRole("link", { name: "TC-1 · Pay with a valid card" });

    expect(readListQueries()[0]).toEqual({
      status: ["open", "fixed", "reopened"],
      storyKey: "TES-1",
    });
  });

  it("clears the filters from the filtered empty state", async () => {
    const user = userEvent.setup();
    respond(() => {
      const isFiltered = readListQueries().at(-1)?.storyKey !== undefined;

      return createSuccessResult(isFiltered ? [] : FAILURES);
    });
    renderPage({ ...EMPTY_FAILURE_FILTERS, storyKey: "SHOP-2" });

    expect(await screen.findByText(empty.noMatch)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: empty.clearFilters }));

    expect(routerReplace).toHaveBeenLastCalledWith(PAGE_PATH, { scroll: false });
    expect(
      await screen.findByRole("link", { name: "TC-1 · Pay with a valid card" }),
    ).toBeInTheDocument();
  });

  it("shows the plain empty state without filters", async () => {
    respond(createSuccessResult([]));
    renderPage();

    expect(await screen.findByText(empty.title)).toBeInTheDocument();
    expect(screen.getByText(empty.description)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: empty.clearFilters })).not.toBeInTheDocument();
  });

  it("retries after a load error", async () => {
    const user = userEvent.setup();
    let isFailing = true;
    respond(() => {
      return isFailing ? createErrorResult(500, "CONFLICT") : createSuccessResult(FAILURES);
    });
    renderPage();

    expect(await screen.findByText(englishFailures.loadError)).toBeInTheDocument();
    isFailing = false;
    await user.click(screen.getByRole("button", { name: englishFailures.retry }));

    expect(
      await screen.findByRole("link", { name: "TC-1 · Pay with a valid card" }),
    ).toBeInTheDocument();
  });
});
