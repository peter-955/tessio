import englishTestCases from "@/lib/i18n/locales/en/testCases.json";
import { tabTo } from "@/test/utils/tab-to.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { NewTestCasePage } from "./new-test-case";
import { apiGet, apiPost } from "./test/mocks/api-client.mock";
import { routerReplace, setNavigation } from "./test/mocks/next-navigation.mock";
import {
  createCreatedResult,
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "./test/utils/api-result.util";
import { interpolate } from "./test/utils/interpolate.util";
import { buildProject, QC_CAPABILITIES } from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { openSelectOption } from "./test/utils/select-option.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import {
  buildStoryDetail,
  buildStorySummary,
  buildTestCaseDetail,
  SECOND_CRITERION_ID,
} from "./test/utils/test-case-fixture.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const CREATE_PATH = "/api/projects/{project_key}/test-cases";
const STORIES_PATH = "/api/projects/{project_key}/stories";
const STORY_PATH = "/api/projects/{project_key}/stories/{jira_key}";
const TEST_DATA_PATH = "/api/projects/{project_key}/test-data";

const { actions, detail, errors, form, toasts } = englishTestCases;

const renderPage = (
  initialStoryKey: string | null,
  capabilities = QC_CAPABILITIES,
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(
    <NewTestCasePage initialStoryKey={initialStoryKey} />,
    buildProject({ capabilities }),
  );
};

const fillCase = async (user: UserEvent): Promise<void> => {
  await user.type(screen.getByRole("textbox", { name: new RegExp(`^${form.title}`) }), "Refund");
  await user.type(
    screen.getByRole("textbox", { name: new RegExp(`^${form.action}`) }),
    "Refund it",
  );
};

describe("NewTestCasePage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    routerReplace.mockReset();
    setNavigation("/projects/SHOP/test-cases/new");
    respondWithRoutes(apiGet, {
      [STORIES_PATH]: createSuccessResult([buildStorySummary()]),
      [STORY_PATH]: createSuccessResult(buildStoryDetail()),
      [TEST_DATA_PATH]: createSuccessResult([]),
    });
    respondWithRoutes(apiPost, {
      [CREATE_PATH]: createCreatedResult(buildTestCaseDetail({ code: "TC-7" })),
    });
  });

  it("creates a case and opens it", async () => {
    const user = userEvent.setup();
    renderPage(null);

    await user.click(
      await openSelectOption(user, new RegExp(`^${form.story}`), "SHOP-1 · Pay by card"),
    );
    await fillCase(user);
    await user.click(
      await openSelectOption(
        user,
        new RegExp(`^${form.criteria}`),
        "AC2 · Declined card shows an error",
      ),
    );
    await user.click(screen.getByRole("button", { name: form.addStep }));
    await user.type(
      within(screen.getAllByRole("listitem")[1] as HTMLElement).getByRole("textbox", {
        name: new RegExp(`^${form.action}`),
      }),
      "Check the email",
    );
    await user.click(screen.getByRole("button", { name: actions.create }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(CREATE_PATH, {
        params: { path: { project_key: "SHOP" } },
        body: {
          storyKey: "SHOP-1",
          title: "Refund",
          priority: "medium",
          businessValue: null,
          preconditions: null,
          steps: [
            { action: "Refund it", expected: null },
            { action: "Check the email", expected: null },
          ],
          criterionIds: [SECOND_CRITERION_ID],
        },
      });
    });
    expect(
      await screen.findByText(interpolate(toasts.created, { code: "TC-7" })),
    ).toBeInTheDocument();
    expect(routerReplace).toHaveBeenCalledWith("/projects/SHOP/test-cases/TC-7");
  });

  it("locks the story that came from the URL", async () => {
    const user = userEvent.setup();
    renderPage("SHOP-1");

    expect(screen.getByRole("combobox", { name: new RegExp(`^${form.story}`) })).toBeDisabled();
    await fillCase(user);
    await user.click(screen.getByRole("button", { name: actions.create }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(
        CREATE_PATH,
        expect.objectContaining({ body: expect.objectContaining({ storyKey: "SHOP-1" }) }),
      );
    });
  });

  it("shows the required errors and sends nothing", async () => {
    const user = userEvent.setup();
    renderPage(null);

    await user.click(screen.getByRole("button", { name: actions.create }));

    expect(await screen.findAllByText(form.required)).toHaveLength(3);
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("explains a criterion that cannot be linked", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, { [CREATE_PATH]: createErrorResult(422, "INVALID_REQUEST") });
    renderPage("SHOP-1");

    await fillCase(user);
    await user.click(screen.getByRole("button", { name: actions.create }));

    expect(await screen.findByText(errors.criterionNotLinkable)).toBeInTheDocument();
    expect(routerReplace).not.toHaveBeenCalled();
  });

  it("tells a viewer they can't create cases", () => {
    renderPage(null, buildProject().capabilities);

    expect(screen.getByText(detail.cannotCreate)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: actions.create })).toBeNull();
  });

  it("has no axe violations, links the required errors and creates from the keyboard", async () => {
    const user = userEvent.setup();
    const { container } = renderPage("SHOP-1");

    expect(
      await screen.findByRole("textbox", { name: new RegExp(`^${form.title}`) }),
    ).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();

    const createButton = screen.getByRole("button", { name: actions.create });
    await user.click(createButton);
    const titleInput = screen.getByRole("textbox", { name: new RegExp(`^${form.title}`) });
    await waitFor(() => {
      expect(titleInput).toHaveAccessibleDescription(form.required);
    });
    expect(titleInput).toHaveAttribute("aria-invalid", "true");
    expect(await axe(container)).toHaveNoViolations();

    await fillCase(user);
    await tabTo(user, createButton);
    await user.keyboard("{Enter}");

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(
        CREATE_PATH,
        expect.objectContaining({ body: expect.objectContaining({ title: "Refund" }) }),
      );
    });
  });
});
