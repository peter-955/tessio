import englishSprints from "@/lib/i18n/locales/en/sprints.json";
import englishStories from "@/lib/i18n/locales/en/stories.json";
import { buildStorySummary } from "@/modules/stories/test/utils/story-fixture.util";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { SprintDetailPage } from "./sprint-detail";
import { apiGet } from "./test/mocks/api-client.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "./test/utils/api-result.util";
import { buildProject } from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { ACTIVE_SPRINT_ID, buildSprint } from "./test/utils/sprint-fixture.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface StoryListRequest {
  params: { query: Record<string, string> };
}

const SPRINT_PATH = "/api/projects/{project_key}/sprints/{sprint_id}";
const STORIES_PATH = "/api/projects/{project_key}/stories";
const SYNC_PATH = "/api/projects/{project_key}/sync";

const { detail } = englishSprints;

const respond = (sprint: ApiResult | (() => ApiResult), stories: ApiResult): void => {
  respondWithRoutes(apiGet, {
    [SPRINT_PATH]: sprint,
    [STORIES_PATH]: stories,
    [SYNC_PATH]: createSuccessResult({
      status: "never",
      queuedAt: null,
      startedAt: null,
      finishedAt: null,
      lastSucceededAt: null,
      errorCode: null,
    }),
  });
};

const readListQueries = (): Record<string, string>[] => {
  return apiGet.mock.calls
    .filter(([path]) => {
      return path === STORIES_PATH;
    })
    .map(([, options]) => {
      return (options as StoryListRequest).params.query;
    });
};

describe("SprintDetailPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    respond(createSuccessResult(buildSprint()), createSuccessResult([buildStorySummary()]));
  });

  it("shows the sprint header and its stories", async () => {
    const { container } = renderWithProject(
      <SprintDetailPage sprintId={ACTIVE_SPRINT_ID} />,
      buildProject(),
    );

    expect(await screen.findByRole("heading", { level: 1, name: "Sprint 12" })).toBeVisible();
    expect(screen.getByText(englishSprints.states.active)).toBeInTheDocument();
    expect(screen.getByText("Oct 14, 2026 – Oct 28, 2026")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: detail.back })).toHaveAttribute(
      "href",
      "/projects/SHOP/sprints",
    );
    expect(screen.getByRole("heading", { level: 2, name: detail.storiesTitle })).toBeVisible();
    expect(await screen.findByRole("link", { name: "SHOP-1" })).toBeInTheDocument();
    expect(readListQueries()[0]).toEqual({ sprintId: ACTIVE_SPRINT_ID });
    expect(screen.queryByRole("columnheader", { name: englishStories.columns.sprint })).toBeNull();
    expect(screen.queryByRole("combobox", { name: englishStories.filters.sprint })).toBeNull();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("keeps the sprint when filtering by status", async () => {
    const user = userEvent.setup();
    renderWithProject(<SprintDetailPage sprintId={ACTIVE_SPRINT_ID} />, buildProject());
    await screen.findByRole("link", { name: "SHOP-1" });

    await user.type(screen.getByRole("textbox", { name: englishStories.filters.search }), "card");

    await waitFor(() => {
      expect(readListQueries()).toContainEqual({ sprintId: ACTIVE_SPRINT_ID, query: "card" });
    });
  });

  it("shows the sprint empty state without filters", async () => {
    respond(createSuccessResult(buildSprint()), createSuccessResult([]));
    renderWithProject(<SprintDetailPage sprintId={ACTIVE_SPRINT_ID} />, buildProject());

    expect(await screen.findByText(englishStories.empty.title)).toBeInTheDocument();
  });

  it("shows the not found view for an unknown sprint", async () => {
    respond(() => {
      return createErrorResult(404, "NOT_FOUND");
    }, createSuccessResult([]));
    const { container } = renderWithProject(
      <SprintDetailPage sprintId={ACTIVE_SPRINT_ID} />,
      buildProject(),
    );

    expect(await screen.findByText(detail.notFound.title)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: detail.back })).toHaveAttribute(
      "href",
      "/projects/SHOP/sprints",
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the not found view for a malformed id without a request", () => {
    renderWithProject(<SprintDetailPage sprintId="not-a-uuid" />, buildProject());

    expect(screen.getByText(detail.notFound.title)).toBeInTheDocument();
    expect(apiGet).not.toHaveBeenCalledWith(SPRINT_PATH, expect.anything());
  });

  it("shows an error with retry for other failures", async () => {
    respond(() => {
      return createErrorResult(500, "CONFLICT");
    }, createSuccessResult([]));
    renderWithProject(<SprintDetailPage sprintId={ACTIVE_SPRINT_ID} />, buildProject());

    expect(await screen.findByText(detail.loadError)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: englishSprints.retry })).toBeInTheDocument();
  });
});
