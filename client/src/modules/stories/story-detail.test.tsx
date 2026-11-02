import englishStories from "@/lib/i18n/locales/en/stories.json";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { StoryDetailPage } from "./story-detail";
import { apiGet, apiPatch, apiPut } from "./test/mocks/api-client.mock";
import { routerReplace, setNavigation } from "./test/mocks/next-navigation.mock";
import { HEADING_BULLET_LIST_DOCUMENT } from "./test/utils/adf-fixture.util";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "./test/utils/api-result.util";
import { interpolate } from "./test/utils/interpolate.util";
import {
  buildProject,
  DEV_CAPABILITIES,
  QC_CAPABILITIES,
  VIEWER_CAPABILITIES,
} from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import {
  ACTIVE_SPRINT_ID,
  buildCriterion,
  buildStoryDetail,
  buildSyncState,
} from "./test/utils/story-fixture.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import { StoryDetailTab } from "./typing/enums/story-detail-tab.enum";
import type { StoryDetailSlots } from "./typing/types/story-detail-slots.type";
import type { StoryDetail } from "./typing/types/story.type";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const STORY_PATH = "/api/projects/{project_key}/stories/{jira_key}";
const TEST_STATUS_PATH = "/api/projects/{project_key}/stories/{jira_key}/test-status";
const STORIES_PATH = "/api/projects/{project_key}/stories";
const STORY_PAGE_PATH = "/projects/SHOP/stories/SHOP-1";

const { actions, confirm, criteria, detail, tabs, toasts, testStatuses, errors } = englishStories;

const STORY = buildStoryDetail({
  description: HEADING_BULLET_LIST_DOCUMENT,
  criteria: [
    buildCriterion({
      id: "d1000000-0000-4000-8000-000000000003",
      code: "AC-3",
      position: 3,
      text: "Old rule",
      isRemoved: true,
      removedAt: "2026-10-18T09:00:00Z",
    }),
    buildCriterion({
      id: "d1000000-0000-4000-8000-000000000002",
      code: "AC-2",
      position: 2,
      text: "Declined card shows an error",
    }),
    buildCriterion(),
  ],
});

const respondWithStory = (story: StoryDetail | (() => ApiResult)): void => {
  respondWithRoutes(apiGet, {
    [STORY_PATH]: typeof story === "function" ? story : createSuccessResult(story),
    [STORIES_PATH]: createSuccessResult([]),
    "/api/projects/{project_key}/sync": createSuccessResult(buildSyncState()),
  });
};

const renderPage = (
  capabilities = VIEWER_CAPABILITIES,
  options: { initialTab?: StoryDetailTab; slots?: StoryDetailSlots; jiraKey?: string } = {},
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(
    <StoryDetailPage
      jiraKey={options.jiraKey ?? "shop-1"}
      initialTab={options.initialTab ?? StoryDetailTab.OVERVIEW}
      slots={options.slots ?? {}}
    />,
    buildProject({ capabilities }),
  );
};

const queryActionButtons = (): HTMLElement[] => {
  return Object.values(actions).flatMap((label) => {
    return screen.queryAllByRole("button", { name: label });
  });
};

describe("StoryDetailPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPut.mockReset();
    routerReplace.mockReset();
    setNavigation(STORY_PAGE_PATH);
    respondWithStory(STORY);
  });

  it("shows the header, description and criteria", async () => {
    const { container } = renderPage();

    expect(
      await screen.findByRole("heading", { level: 1, name: "SHOP-1 · Pay by card" }),
    ).toBeInTheDocument();
    expect(apiGet).toHaveBeenCalledWith(STORY_PATH, {
      params: { path: { project_key: "SHOP", jira_key: "SHOP-1" } },
      signal: expect.any(AbortSignal),
    });
    expect(screen.getByText("Story")).toBeInTheDocument();
    expect(screen.getByText("In Progress")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Sprint 12" })).toHaveAttribute(
      "href",
      `/projects/SHOP/sprints/${ACTIVE_SPRINT_ID}`,
    );
    expect(screen.getByRole("link", { name: detail.back })).toHaveAttribute(
      "href",
      "/projects/SHOP/stories",
    );
    expect(screen.getByRole("link", { name: detail.openInJira })).toHaveAttribute(
      "href",
      "https://shop.atlassian.net/browse/SHOP-1",
    );
    expect(screen.getByRole("heading", { level: 3, name: "Acceptance Criteria" })).toBeVisible();

    const criteriaItems = within(
      screen.getByRole("heading", { name: criteria.title }).parentElement as HTMLElement,
    ).getAllByRole("listitem");
    expect(criteriaItems.map((item) => item.textContent)).toEqual([
      "AC-1Card payment succeeds",
      "AC-2Declined card shows an error",
      `AC-3Old rule${interpolate(criteria.removed, { date: "Oct 18, 2026" })}`,
    ]);
    expect(screen.getByText("Old rule").tagName).toBe("S");
    expect(screen.queryByRole("tab", { name: tabs.testCases })).toBeNull();
    expect(screen.getAllByRole("tab")).toHaveLength(1);
    expect(queryActionButtons()).toEqual([]);
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the empty description, empty criteria and missing alert", async () => {
    respondWithStory(
      buildStoryDetail({ criteria: [], sprint: null, jiraMissingAt: "2026-10-18T09:00:00Z" }),
    );
    renderPage();

    expect(await screen.findByText(englishStories.description.empty)).toBeInTheDocument();
    expect(screen.getByText(criteria.empty.title)).toBeInTheDocument();
    expect(screen.getByText(detail.noSprint)).toBeInTheDocument();
    const alert = screen.getByText(detail.missing.title).closest('[role="alert"]');
    expect(alert).not.toBeNull();
    expect(
      within(alert as HTMLElement).getByText(
        interpolate(detail.missing.body, { date: "Oct 18, 2026" }),
      ),
    ).toBeInTheDocument();
  });

  it("lets a developer mark the story ready for test", async () => {
    const user = userEvent.setup();
    respondWithStory(buildStoryDetail({ availableTestStatuses: ["ready_for_test"] }));
    respondWithRoutes(apiPut, {
      [TEST_STATUS_PATH]: createSuccessResult(
        buildStoryDetail({ testStatus: "ready_for_test", availableTestStatuses: ["not_started"] }),
      ),
    });
    renderPage(DEV_CAPABILITIES);

    const button = await screen.findByRole("button", { name: actions.markReadyForTest });
    expect(queryActionButtons()).toEqual([button]);
    await user.click(button);

    expect(apiPut).toHaveBeenCalledWith(TEST_STATUS_PATH, {
      params: { path: { project_key: "SHOP", jira_key: "SHOP-1" } },
      body: { testStatus: "ready_for_test" },
    });
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(
      await screen.findByText(
        interpolate(toasts.statusChanged, { status: testStatuses.ready_for_test }),
      ),
    ).toBeInTheDocument();
    expect(await screen.findByRole("button", { name: actions.markNotStarted })).toBeInTheDocument();
  });

  it("asks QC to confirm before marking passed", async () => {
    const user = userEvent.setup();
    respondWithStory(
      buildStoryDetail({ testStatus: "in_test", availableTestStatuses: ["failed", "passed"] }),
    );
    respondWithRoutes(apiPut, {
      [TEST_STATUS_PATH]: createSuccessResult(
        buildStoryDetail({ testStatus: "passed", availableTestStatuses: ["failed"] }),
      ),
    });
    renderPage(QC_CAPABILITIES);

    await screen.findByRole("button", { name: actions.markPassed });
    expect(queryActionButtons().map((button) => button.textContent)).toEqual([
      actions.markPassed,
      actions.markFailed,
    ]);
    await user.click(screen.getByRole("button", { name: actions.markPassed }));

    const dialog = await screen.findByRole("dialog", {
      name: interpolate(confirm.passed.title, { jiraKey: "SHOP-1" }),
    });
    expect(within(dialog).getByText(confirm.passed.message)).toBeInTheDocument();
    expect(apiPut).not.toHaveBeenCalled();
    await user.click(within(dialog).getByRole("button", { name: actions.markPassed }));

    expect(apiPut).toHaveBeenCalledWith(TEST_STATUS_PATH, {
      params: { path: { project_key: "SHOP", jira_key: "SHOP-1" } },
      body: { testStatus: "passed" },
    });
    expect(
      await screen.findByText(interpolate(toasts.statusChanged, { status: testStatuses.passed })),
    ).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.queryByRole("dialog")).toBeNull();
    });
  });

  it("cancels the confirmation without a request", async () => {
    const user = userEvent.setup();
    respondWithStory(buildStoryDetail({ testStatus: "passed", availableTestStatuses: ["failed"] }));
    renderPage(QC_CAPABILITIES);

    await user.click(await screen.findByRole("button", { name: actions.markFailed }));
    const dialog = await screen.findByRole("dialog");
    await user.click(within(dialog).getByRole("button", { name: "Cancel" }));

    await waitFor(() => {
      expect(screen.queryByRole("dialog")).toBeNull();
    });
    expect(apiPut).not.toHaveBeenCalled();
  });

  it("shows the sign-off blocked message and refreshes the story", async () => {
    const user = userEvent.setup();
    respondWithStory(
      buildStoryDetail({ testStatus: "in_test", availableTestStatuses: ["passed", "failed"] }),
    );
    respondWithRoutes(apiPut, {
      [TEST_STATUS_PATH]: createErrorResult(409, "STORY_SIGN_OFF_BLOCKED"),
    });
    renderPage(QC_CAPABILITIES);
    await user.click(await screen.findByRole("button", { name: actions.markPassed }));
    const storyRequestCount = apiGet.mock.calls.filter(([path]) => path === STORY_PATH).length;

    await user.click(
      within(await screen.findByRole("dialog")).getByRole("button", { name: actions.markPassed }),
    );

    expect(await screen.findByText(errors.signOffBlocked)).toBeInTheDocument();
    await waitFor(() => {
      expect(apiGet.mock.calls.filter(([path]) => path === STORY_PATH).length).toBeGreaterThan(
        storyRequestCount,
      );
    });
  });

  it("shows the invalid transition message", async () => {
    const user = userEvent.setup();
    respondWithStory(buildStoryDetail({ availableTestStatuses: ["ready_for_test"] }));
    respondWithRoutes(apiPut, {
      [TEST_STATUS_PATH]: createErrorResult(409, "INVALID_STATUS_TRANSITION"),
    });
    renderPage(DEV_CAPABILITIES);

    await user.click(await screen.findByRole("button", { name: actions.markReadyForTest }));

    expect(await screen.findByText(errors.invalidTransition)).toBeInTheDocument();
  });

  it("shows the not found view", async () => {
    respondWithStory(() => {
      return createErrorResult(404, "NOT_FOUND");
    });
    renderPage();

    expect(await screen.findByText(detail.notFound.title)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: detail.back })).toHaveAttribute(
      "href",
      "/projects/SHOP/stories",
    );
  });

  it("shows an error with retry for other failures", async () => {
    respondWithStory(() => {
      return createErrorResult(500, "CONFLICT");
    });
    renderPage();

    expect(await screen.findByText(detail.loadError)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: englishStories.retry })).toBeInTheDocument();
  });

  it("adds a tab per slot in the fixed order and selects the initial tab", async () => {
    const user = userEvent.setup();
    const { container } = renderPage(VIEWER_CAPABILITIES, {
      initialTab: StoryDetailTab.GAPS,
      slots: {
        [StoryDetailTab.GAPS]: <p>Gaps panel</p>,
        [StoryDetailTab.TEST_CASES]: <p>Test cases panel</p>,
      },
    });

    expect(await screen.findByText("Gaps panel")).toBeInTheDocument();
    expect(screen.getAllByRole("tab").map((tab) => tab.textContent)).toEqual([
      tabs.overview,
      tabs.testCases,
      tabs.gaps,
    ]);
    expect(screen.getByRole("tab", { name: tabs.gaps })).toHaveAttribute("aria-selected", "true");
    expect(screen.queryByText("Test cases panel")).toBeNull();
    expect(await axe(container)).toHaveNoViolations();

    await user.click(screen.getByRole("tab", { name: tabs.testCases }));

    expect(await screen.findByText("Test cases panel")).toBeInTheDocument();
    expect(routerReplace).toHaveBeenCalledWith("?tab=test-cases", { scroll: false });
  });

  it("switches the tab when the URL changes without a remount", async () => {
    const slots: StoryDetailSlots = { [StoryDetailTab.GAPS]: <p>Gaps panel</p> };
    const { rerenderWithProject } = renderPage(VIEWER_CAPABILITIES, { slots });
    await screen.findByRole("tab", { name: tabs.overview });
    expect(screen.queryByText("Gaps panel")).toBeNull();

    setNavigation(STORY_PAGE_PATH, `tab=${StoryDetailTab.GAPS}`);
    rerenderWithProject(
      <StoryDetailPage jiraKey="shop-1" initialTab={StoryDetailTab.OVERVIEW} slots={slots} />,
    );

    expect(await screen.findByText("Gaps panel")).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: tabs.gaps })).toHaveAttribute("aria-selected", "true");
    expect(routerReplace).not.toHaveBeenCalled();
  });

  it("lets a QC edit a story written in Tessio", async () => {
    const user = userEvent.setup();
    const writtenStory = buildStoryDetail({
      source: "tessio",
      jiraUrl: "",
      jiraStatus: "",
      sprint: null,
      descriptionText: "As a buyer",
      criteria: [buildCriterion()],
    });
    respondWithStory(writtenStory);
    respondWithRoutes(apiPatch, {
      [STORY_PATH]: createSuccessResult({ ...writtenStory, title: "Pay by voucher" }),
    });
    renderWithProject(
      <StoryDetailPage jiraKey="shop-1" initialTab={StoryDetailTab.OVERVIEW} slots={{}} />,
      buildProject({
        jiraProjectKey: null,
        jiraBoardId: null,
        isLinkedToJira: false,
        capabilities: [...QC_CAPABILITIES, "story.edit"],
      }),
    );

    expect(await screen.findByText(detail.writtenInTessio)).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: detail.openInJira })).toBeNull();
    await user.click(screen.getByRole("button", { name: englishStories.editor.edit }));
    const dialog = await screen.findByRole("dialog");
    const titleField = within(dialog).getByRole("textbox", { name: /^Title/ });
    await user.clear(titleField);
    await user.type(titleField, "Pay by voucher");
    await user.click(within(dialog).getByRole("button", { name: englishStories.editor.save }));

    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledWith(STORY_PATH, {
        params: { path: { project_key: "SHOP", jira_key: "SHOP-1" } },
        body: {
          title: "Pay by voucher",
          description: "As a buyer",
          criteria: [writtenStory.criteria[0]?.text],
        },
      });
    });
  });
});
