import englishRuns from "@/lib/i18n/locales/en/runs.json";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "@/modules/auth/test/utils/api-result.util";
import { screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet } from "../../test/mocks/api-client.mock";
import { renderWithProject } from "../../test/utils/render-with-project.util";
import { createRunSummary } from "../../test/utils/run.fixture";
import { StoryRuns } from "./story-runs";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("@/modules/auth/test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface ListRequest {
  params: { query: Record<string, string | number> };
}

const RUNS_PATH = "/api/projects/{project_key}/runs";

const { empty, table } = englishRuns;

describe("StoryRuns", () => {
  beforeEach(() => {
    apiGet.mockReset();
    respondWithRoutes(apiGet, { [RUNS_PATH]: createSuccessResult([createRunSummary()]) });
  });

  it("lists the story's runs without a story column and links to all its runs", async () => {
    const { container } = renderWithProject(<StoryRuns jiraKey="APP-1" />);

    const runsTable = await screen.findByRole("table", { name: table.label });
    expect(
      within(runsTable).queryByRole("columnheader", { name: table.story }),
    ).not.toBeInTheDocument();
    expect(within(runsTable).queryByText("APP-1 · Pay by card")).not.toBeInTheDocument();
    expect(within(runsTable).getByText("Staging")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: empty.viewAll })).toHaveAttribute(
      "href",
      "/projects/APP/runs?story=APP-1",
    );
    const [, options] = apiGet.mock.calls[0];
    expect((options as ListRequest).params.query).toEqual({ storyKey: "APP-1", limit: 50 });
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the story empty state", async () => {
    respondWithRoutes(apiGet, { [RUNS_PATH]: createSuccessResult([]) });
    renderWithProject(<StoryRuns jiraKey="APP-1" />);

    expect(await screen.findByText(empty.storyTitle)).toBeInTheDocument();
    expect(screen.getByText(empty.storyDescription)).toBeInTheDocument();
  });

  it("shows the story empty state when the story is no longer known", async () => {
    respondWithRoutes(apiGet, { [RUNS_PATH]: createErrorResult(404, "NOT_FOUND") });
    renderWithProject(<StoryRuns jiraKey="APP-1" />);

    expect(await screen.findByText(empty.storyTitle)).toBeInTheDocument();
    expect(screen.queryByText(englishRuns.loadError)).not.toBeInTheDocument();
  });
});
