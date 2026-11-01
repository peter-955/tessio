import englishTestCases from "@/lib/i18n/locales/en/testCases.json";
import englishTraceability from "@/lib/i18n/locales/en/traceability.json";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { StoryTestCases } from "./story-test-cases";
import { apiGet } from "./test/mocks/api-client.mock";
import { routerReplace, setNavigation } from "./test/mocks/next-navigation.mock";
import { createSuccessResult, respondWithRoutes } from "./test/utils/api-result.util";
import { buildCaseLatestResult } from "./test/utils/case-latest-result-fixture.util";
import { buildProject, QC_CAPABILITIES } from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { openSelectOption } from "./test/utils/select-option.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import { buildStoryDetail, buildTestCaseSummary } from "./test/utils/test-case-fixture.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface ListRequest {
  params: { query: Record<string, string | boolean> };
}

const TEST_CASES_PATH = "/api/projects/{project_key}/test-cases";
const STORY_PATH = "/api/projects/{project_key}/stories/{jira_key}";
const LATEST_RESULTS_PATH = "/api/projects/{project_key}/case-latest-results";

const { actions, empty, filters, priority, table } = englishTestCases;

const readListQueries = (): Record<string, string | boolean>[] => {
  return apiGet.mock.calls
    .filter(([path]) => path === TEST_CASES_PATH)
    .map(([, options]) => (options as ListRequest).params.query);
};

describe("StoryTestCases", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    routerReplace.mockReset();
    setNavigation("/projects/SHOP/stories/SHOP-1", "tab=test-cases");
    respondWithRoutes(apiGet, {
      [TEST_CASES_PATH]: createSuccessResult([buildTestCaseSummary()]),
      [STORY_PATH]: createSuccessResult(buildStoryDetail()),
      [LATEST_RESULTS_PATH]: createSuccessResult([buildCaseLatestResult()]),
    });
  });

  it("lists the story's cases without a story column or filter", async () => {
    const { container } = renderWithProject(
      <StoryTestCases jiraKey="SHOP-1" />,
      buildProject({ capabilities: QC_CAPABILITIES }),
    );

    expect(await screen.findByRole("link", { name: "TC-1" })).toBeInTheDocument();
    expect(readListQueries()[0]).toEqual({ storyKey: "SHOP-1" });
    expect(await screen.findByText(englishTraceability.resultStatus.failed)).toBeInTheDocument();
    expect(
      apiGet.mock.calls
        .filter(([path]) => path === LATEST_RESULTS_PATH)
        .map(([, options]) => (options as ListRequest).params.query),
    ).toEqual([{ storyKey: "SHOP-1" }]);
    expect(screen.queryByRole("columnheader", { name: table.story })).toBeNull();
    expect(screen.queryByRole("combobox", { name: new RegExp(`^${filters.story}`) })).toBeNull();
    expect(screen.getByRole("link", { name: actions.new })).toHaveAttribute(
      "href",
      "/projects/SHOP/test-cases/new?story=SHOP-1",
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it("filters inside the story without touching the URL", async () => {
    const user = userEvent.setup();
    renderWithProject(
      <StoryTestCases jiraKey="SHOP-1" />,
      buildProject({ capabilities: QC_CAPABILITIES }),
    );

    await screen.findByRole("link", { name: "TC-1" });
    await user.click(
      await openSelectOption(user, new RegExp(`^${filters.priority}`), priority.critical),
    );

    await waitFor(() => {
      expect(readListQueries().at(-1)).toEqual({ storyKey: "SHOP-1", priority: "critical" });
    });
    expect(routerReplace).not.toHaveBeenCalled();
  });

  it("shows the empty state without New for a viewer", async () => {
    respondWithRoutes(apiGet, {
      [TEST_CASES_PATH]: createSuccessResult([]),
      [STORY_PATH]: createSuccessResult(buildStoryDetail()),
      [LATEST_RESULTS_PATH]: createSuccessResult([buildCaseLatestResult()]),
    });
    renderWithProject(<StoryTestCases jiraKey="SHOP-1" />, buildProject());

    expect(await screen.findByText(empty.title)).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: actions.new })).toBeNull();
  });
});
