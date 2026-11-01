import englishSprints from "@/lib/i18n/locales/en/sprints.json";
import englishStories from "@/lib/i18n/locales/en/stories.json";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { SprintsPage } from "./sprints";
import { apiGet } from "./test/mocks/api-client.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "./test/utils/api-result.util";
import { ADMIN_CAPABILITIES, buildProject } from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { buildSprint, CLOSED_SPRINT_ID, FUTURE_SPRINT_ID } from "./test/utils/sprint-fixture.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const SPRINTS_PATH = "/api/projects/{project_key}/sprints";
const SYNC_PATH = "/api/projects/{project_key}/sync";

const { columns, states, empty } = englishSprints;

const SPRINTS = [
  buildSprint(),
  buildSprint({
    id: FUTURE_SPRINT_ID,
    jiraSprintId: 13,
    name: "Sprint 13",
    state: "future",
    startAt: null,
    endAt: null,
    storyCount: 0,
  }),
  buildSprint({
    id: CLOSED_SPRINT_ID,
    jiraSprintId: 11,
    name: "Sprint 11",
    state: "closed",
    startAt: "2026-09-30T00:00:00Z",
    endAt: "2026-10-14T00:00:00Z",
    completeAt: "2026-10-13T16:00:00Z",
    storyCount: 7,
  }),
];

const respond = (sprints: ApiResult | (() => ApiResult)): void => {
  respondWithRoutes(apiGet, {
    [SPRINTS_PATH]: sprints,
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

const readRow = (name: string): HTMLElement => {
  return screen.getByRole("link", { name }).closest("tr") as HTMLElement;
};

describe("SprintsPage", () => {
  beforeEach(() => {
    apiGet.mockReset();
    respond(createSuccessResult(SPRINTS));
  });

  it("lists sprints in server order with state, dates and story count", async () => {
    const { container } = renderWithProject(
      <SprintsPage />,
      buildProject({ capabilities: ADMIN_CAPABILITIES }),
    );

    expect(await screen.findByRole("link", { name: "Sprint 12" })).toHaveAttribute(
      "href",
      "/projects/SHOP/sprints/5a1e2b3c-4d5e-4f60-8a1b-2c3d4e5f6a70",
    );
    expect(screen.getAllByRole("columnheader").map((header) => header.textContent)).toEqual([
      columns.name,
      columns.state,
      columns.dates,
      columns.stories,
    ]);
    expect(screen.getAllByRole("rowheader").map((header) => header.textContent)).toEqual([
      "Sprint 12",
      "Sprint 13",
      "Sprint 11",
    ]);

    const activeRow = within(readRow("Sprint 12"));
    expect(activeRow.getByText(states.active)).toBeInTheDocument();
    expect(activeRow.getByText("Oct 14, 2026 – Oct 28, 2026")).toBeInTheDocument();
    expect(activeRow.getByText("4")).toBeInTheDocument();

    const futureRow = within(readRow("Sprint 13"));
    expect(futureRow.getByText(states.future)).toBeInTheDocument();
    expect(futureRow.getByText(englishSprints.dates.notSet)).toBeInTheDocument();

    const closedRow = within(readRow("Sprint 11"));
    expect(closedRow.getByText(states.closed)).toBeInTheDocument();
    expect(closedRow.getByText("Completed Oct 13, 2026")).toBeInTheDocument();
    expect(closedRow.getByText("7")).toBeInTheDocument();

    expect(screen.getByRole("button", { name: englishStories.sync.action })).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the empty state", async () => {
    respond(createSuccessResult([]));
    const { container } = renderWithProject(<SprintsPage />, buildProject());

    expect(await screen.findByText(empty.title)).toBeInTheDocument();
    expect(screen.getByText(empty.description)).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows an error and retries", async () => {
    const user = userEvent.setup();
    let isFailing = true;
    respond(() => {
      return isFailing ? createErrorResult(500, "CONFLICT") : createSuccessResult(SPRINTS);
    });
    renderWithProject(<SprintsPage />, buildProject());

    expect(await screen.findByText(englishSprints.loadError)).toBeInTheDocument();
    isFailing = false;
    await user.click(screen.getByRole("button", { name: englishSprints.retry }));

    expect(await screen.findByRole("link", { name: "Sprint 12" })).toBeInTheDocument();
  });
});
