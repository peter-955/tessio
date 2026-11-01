import { VIEWER_CAPABILITIES } from "@/components/project-context/test/utils/project-fixture.util";
import englishManualRun from "@/lib/i18n/locales/en/manualRun.json";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { NewManualRunPage } from "./new-manual-run";
import { apiGet, apiPost } from "./test/mocks/api-client.mock";
import { routerReplace } from "./test/mocks/next-navigation.mock";
import {
  createCreatedResult,
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "./test/utils/api-result.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import {
  FIRST_CASE_ID,
  NEW_RUN_ID,
  PRODUCTION_ID,
  SECOND_CASE_ID,
  STAGING_ID,
  buildCreatedRun,
  buildEnvironment,
  buildReadyTestCase,
  buildRunProject,
  buildStory,
} from "./test/utils/run.fixture";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const STORIES_PATH = "/api/projects/{project_key}/stories";
const TEST_CASES_PATH = "/api/projects/{project_key}/test-cases";
const ENVIRONMENTS_PATH = "/api/projects/{project_key}/environments";
const GAPS_PATH = "/api/projects/{project_key}/gaps";
const RUNS_PATH = "/api/projects/{project_key}/runs";

const { errors } = englishManualRun;
const newText = englishManualRun.new;

const READY_CASES = [
  buildReadyTestCase(),
  buildReadyTestCase({ id: SECOND_CASE_ID, code: "TC-2", title: "Pay by voucher", stepCount: 1 }),
];

const renderPage = (
  initialStoryKey: string | null,
  project = buildRunProject({ defaultEnvironmentId: PRODUCTION_ID }),
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(<NewManualRunPage initialStoryKey={initialStoryKey} />, project);
};

const findCaseCheckbox = (code: string): Promise<HTMLElement> => {
  return screen.findByRole("checkbox", { name: new RegExp(`^${code} · `) });
};

const readPostBody = (): unknown => {
  const [, options] = apiPost.mock.calls[0] ?? [];

  return (options as { body: unknown } | undefined)?.body;
};

describe("NewManualRunPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    respondWithRoutes(apiGet, {
      [STORIES_PATH]: createSuccessResult([buildStory()]),
      [TEST_CASES_PATH]: createSuccessResult(READY_CASES),
      [ENVIRONMENTS_PATH]: createSuccessResult([
        buildEnvironment(),
        buildEnvironment({ id: PRODUCTION_ID, name: "Production" }),
      ]),
      [GAPS_PATH]: createSuccessResult([]),
    });
    respondWithRoutes(apiPost, { [RUNS_PATH]: createCreatedResult(buildCreatedRun()) });
  });

  it("prefills the story, checks every Ready case and preselects the project environment", async () => {
    const { container } = renderPage("SHOP-1");

    expect(await findCaseCheckbox("TC-1")).toBeChecked();
    expect(await findCaseCheckbox("TC-2")).toBeChecked();
    expect(screen.getByText("2 of 2 selected")).toBeInTheDocument();
    expect(screen.getByRole("checkbox", { name: /TC-1 · Pay by card · 2 steps/ })).toBeVisible();
    await waitFor(() => {
      expect(
        screen.getByRole("combobox", { name: new RegExp(`^${newText.environment}`) }),
      ).toHaveValue("Production");
    });
    expect(screen.getByRole("combobox", { name: new RegExp(`^${newText.story}`) })).toHaveValue(
      "SHOP-1 · Checkout",
    );
    expect(apiGet).toHaveBeenCalledWith(
      TEST_CASES_PATH,
      expect.objectContaining({
        params: { path: { project_key: "SHOP" }, query: { storyKey: "SHOP-1", status: "ready" } },
      }),
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it("posts only the checked cases and opens the record page", async () => {
    const user = userEvent.setup();
    renderPage("SHOP-1");

    await user.click(await findCaseCheckbox("TC-2"));
    expect(screen.getByText("1 of 2 selected")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByRole("button", { name: newText.start })).toBeEnabled();
    });
    await user.click(screen.getByRole("button", { name: newText.start }));

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith(`/projects/SHOP/runs/${NEW_RUN_ID}/record`);
    });
    expect(readPostBody()).toEqual({
      storyKey: "SHOP-1",
      environmentId: PRODUCTION_ID,
      testCaseIds: [FIRST_CASE_ID],
    });
  });

  it("clears and selects every case with the toggle", async () => {
    const user = userEvent.setup();
    renderPage("SHOP-1");

    await findCaseCheckbox("TC-1");
    await user.click(screen.getByRole("button", { name: newText.clearAll }));
    expect(screen.getByText("0 of 2 selected")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: newText.start })).toBeDisabled();

    await user.click(screen.getByRole("button", { name: newText.selectAll }));
    expect(screen.getByText("2 of 2 selected")).toBeInTheDocument();
  });

  it("uses the only environment when the project has no default", async () => {
    respondWithRoutes(apiGet, {
      [STORIES_PATH]: createSuccessResult([buildStory()]),
      [TEST_CASES_PATH]: createSuccessResult(READY_CASES),
      [ENVIRONMENTS_PATH]: createSuccessResult([buildEnvironment()]),
      [GAPS_PATH]: createSuccessResult([]),
    });
    const user = userEvent.setup();
    renderPage("SHOP-1", buildRunProject());

    await findCaseCheckbox("TC-1");
    await waitFor(() => {
      expect(screen.getByRole("button", { name: newText.start })).toBeEnabled();
    });
    await user.click(screen.getByRole("button", { name: newText.start }));

    await waitFor(() => {
      expect(readPostBody()).toEqual(expect.objectContaining({ environmentId: STAGING_ID }));
    });
  });

  it("shows the open-gaps error inline", async () => {
    respondWithRoutes(apiPost, { [RUNS_PATH]: createErrorResult(409, "OPEN_GAPS_BLOCK_RUN") });
    const user = userEvent.setup();
    renderPage("SHOP-1");

    await findCaseCheckbox("TC-1");
    await waitFor(() => {
      expect(screen.getByRole("button", { name: newText.start })).toBeEnabled();
    });
    await user.click(screen.getByRole("button", { name: newText.start }));

    expect(await screen.findByText(errors.openGaps)).toBeInTheDocument();
    expect(routerReplace).not.toHaveBeenCalled();
  });

  it("shows the no-Ready-cases state with a link to the story's test cases", async () => {
    respondWithRoutes(apiGet, {
      [STORIES_PATH]: createSuccessResult([buildStory()]),
      [TEST_CASES_PATH]: createSuccessResult([]),
      [ENVIRONMENTS_PATH]: createSuccessResult([buildEnvironment()]),
      [GAPS_PATH]: createSuccessResult([]),
    });
    renderPage("SHOP-1");

    expect(await screen.findByText(newText.noReadyCases)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: newText.openTestCases })).toHaveAttribute(
      "href",
      "/projects/SHOP/stories/SHOP-1?tab=test-cases",
    );
    expect(screen.getByRole("button", { name: newText.start })).toBeDisabled();
  });

  it("warns when the project has no active environment", async () => {
    respondWithRoutes(apiGet, {
      [STORIES_PATH]: createSuccessResult([buildStory()]),
      [TEST_CASES_PATH]: createSuccessResult(READY_CASES),
      [ENVIRONMENTS_PATH]: createSuccessResult([]),
      [GAPS_PATH]: createSuccessResult([]),
    });
    renderPage("SHOP-1");

    expect(await screen.findByText(newText.noEnvironments)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: newText.start })).toBeDisabled();
  });

  it("explains that a viewer cannot start manual runs", () => {
    renderPage("SHOP-1", buildRunProject({ capabilities: VIEWER_CAPABILITIES }));

    expect(screen.getByText(newText.cannotStart)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: newText.start })).not.toBeInTheDocument();
  });

  it("hides the form on an archived project", () => {
    renderPage("SHOP-1", buildRunProject({ isArchived: true }));

    expect(screen.getByText(newText.cannotStart)).toBeInTheDocument();
  });
});
