import { ProjectContext } from "@/components/project-context/contexts/project.context";
import {
  VIEWER_CAPABILITIES,
  buildProject,
} from "@/components/project-context/test/utils/project-fixture.util";
import type { Project } from "@/components/project-context/typing/types/project.type";
import englishErrors from "@/lib/i18n/locales/en/errors.json";
import englishJunitImport from "@/lib/i18n/locales/en/junitImport.json";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "@/modules/auth/test/utils/api-result.util";
import { renderWithProviders } from "@/modules/auth/test/utils/render-with-providers.util";
import { stubBrowserApis } from "@/modules/projects/test/utils/stub-browser-apis.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet, apiPost } from "../../test/mocks/api-client.mock";
import { routerPush } from "../../test/mocks/next-navigation.mock";
import {
  IMPORTED_RUN_ID,
  PRODUCTION_ID,
  STAGING_ID,
  SUITE_ID,
  buildEnvironment,
  buildJunitImport,
} from "../../test/utils/junit-import.fixture";
import { ImportJunitButton } from "../import-junit-button/import-junit-button";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("../../test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface ImportCall {
  params: { path: { project_key: string } };
  bodySerializer: () => FormData;
}

const IMPORT_PATH = "/api/projects/{project_key}/runs/import";
const ENVIRONMENTS_PATH = "/api/projects/{project_key}/environments";
const SUITES_PATH = "/api/projects/{project_key}/suites";

const { actions, form, errors, result, unmapped } = englishJunitImport;

const QC_PROJECT = buildProject({
  myRole: "qc",
  capabilities: [...VIEWER_CAPABILITIES, "run.start", "run.record_manual"],
  defaultEnvironmentId: STAGING_ID,
});

const renderButton = (project: Project = QC_PROJECT) => {
  return renderWithProviders(
    <ProjectContext value={project}>
      <ImportJunitButton />
    </ProjectContext>,
  );
};

const openDialog = async (user: UserEvent): Promise<HTMLElement> => {
  await user.click(await screen.findByRole("button", { name: actions.openImport }));

  return screen.findByRole("dialog", { name: form.title });
};

const chooseFile = async (user: UserEvent, dialog: HTMLElement, file: File): Promise<void> => {
  const input = dialog.querySelector<HTMLInputElement>('input[type="file"]') as HTMLInputElement;
  await user.upload(input, file);
};

const readImportForm = (): FormData => {
  const [, options] = apiPost.mock.calls[0];

  return (options as ImportCall).bodySerializer();
};

const JUNIT_FILE = new File(
  ['<testsuites><testcase name="TC-1 pays"/></testsuites>'],
  "results.xml",
  {
    type: "text/xml",
  },
);

describe("ImportJunitButton", () => {
  beforeAll(() => {
    stubBrowserApis();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    routerPush.mockReset();
    respondWithRoutes(apiGet, {
      [ENVIRONMENTS_PATH]: createSuccessResult([
        buildEnvironment(STAGING_ID, "Staging"),
        buildEnvironment(PRODUCTION_ID, "Production"),
      ]),
      [SUITES_PATH]: createSuccessResult([
        {
          id: SUITE_ID,
          name: "Checkout regression",
          description: null,
          caseCount: 3,
          isArchived: false,
          archivedAt: null,
          lastRun: null,
          createdAt: "2026-10-01T09:00:00Z",
        },
      ]),
    });
  });

  it("is hidden without run.start and on an archived project", () => {
    const { unmount } = renderButton(buildProject());
    expect(screen.queryByRole("button", { name: actions.openImport })).not.toBeInTheDocument();
    unmount();

    renderButton({ ...QC_PROJECT, isArchived: true, archivedAt: "2026-11-01T09:00:00Z" });
    expect(screen.queryByRole("button", { name: actions.openImport })).not.toBeInTheDocument();
  });

  it("imports a JUnit file into the default environment and lists the unmapped tests", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, { [IMPORT_PATH]: createSuccessResult(buildJunitImport()) });
    renderButton();

    const dialog = await openDialog(user);
    expect(await within(dialog).findByText(form.description)).toBeInTheDocument();
    expect(
      within(dialog).getByRole("combobox", { name: new RegExp(form.environment) }),
    ).toHaveValue("Staging");
    expect(await axe(dialog)).toHaveNoViolations();

    await chooseFile(user, dialog, JUNIT_FILE);
    expect(within(dialog).getByText("File: results.xml")).toBeInTheDocument();
    await user.click(within(dialog).getByRole("button", { name: actions.import }));

    const resultDialog = await screen.findByRole("dialog", { name: result.heading });
    expect(apiPost).toHaveBeenCalledWith(IMPORT_PATH, {
      params: { path: { project_key: "SHOP" } },
      body: { file: "results.xml", environment: STAGING_ID, suite: null },
      bodySerializer: expect.any(Function) as () => FormData,
    });
    const formData = readImportForm();
    expect((formData.get("file") as File).name).toBe("results.xml");
    expect(formData.get("environment")).toBe(STAGING_ID);
    expect(formData.has("suite")).toBe(false);

    expect(within(resultDialog).getByText(result.title.failed)).toBeInTheDocument();
    expect(
      within(resultDialog).getByText("3 cases: 1 passed, 1 failed, 1 skipped."),
    ).toBeInTheDocument();
    expect(
      within(resultDialog).getByText("4 tests matched a case. 2 tests did not match any case."),
    ).toBeInTheDocument();
    const table = within(resultDialog).getByRole("table");
    expect(within(table).getByText("loads the home page")).toBeInTheDocument();
    expect(within(table).getByText("home.spec.ts")).toBeInTheDocument();
    expect(within(table).getByText(unmapped.reasons.no_case_code)).toBeInTheDocument();
    expect(within(table).getByText(unmapped.reasons.unknown_case)).toBeInTheDocument();
    expect(await axe(resultDialog)).toHaveNoViolations();

    await user.click(within(resultDialog).getByRole("button", { name: actions.openRun }));
    expect(routerPush).toHaveBeenCalledWith(`/projects/SHOP/runs/${IMPORTED_RUN_ID}`);
  });

  it("sends the chosen environment and suite", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [IMPORT_PATH]: createSuccessResult(
        buildJunitImport({ status: "passed", unmappedTestCount: 0, unmappedTests: [] }),
      ),
    });
    renderButton();

    const dialog = await openDialog(user);
    await user.click(
      await within(dialog).findByRole("combobox", { name: new RegExp(form.environment) }),
    );
    await user.click(await screen.findByRole("option", { name: "Production", hidden: true }));
    await user.click(within(dialog).getByRole("combobox", { name: form.suite }));
    await user.click(
      await screen.findByRole("option", { name: "Checkout regression", hidden: true }),
    );
    await chooseFile(user, dialog, JUNIT_FILE);
    await user.click(within(dialog).getByRole("button", { name: actions.import }));

    const resultDialog = await screen.findByRole("dialog", { name: result.heading });
    expect(within(resultDialog).getByText(result.title.passed)).toBeInTheDocument();
    expect(within(resultDialog).queryByRole("table")).not.toBeInTheDocument();
    const formData = readImportForm();
    expect(formData.get("environment")).toBe(PRODUCTION_ID);
    expect(formData.get("suite")).toBe(SUITE_ID);
  });

  it("refuses a file that is not XML or is over 10 MB before sending", async () => {
    const user = userEvent.setup({ applyAccept: false });
    renderButton();

    const dialog = await openDialog(user);
    await within(dialog).findByText(form.description);
    await chooseFile(user, dialog, new File(["{}"], "results.json", { type: "application/json" }));
    expect(await within(dialog).findByText(errors.notXml)).toBeInTheDocument();

    const largeFile = new File(["x"], "results.xml", { type: "text/xml" });
    Object.defineProperty(largeFile, "size", { value: 10 * 1024 * 1024 + 1 });
    await chooseFile(user, dialog, largeFile);
    expect(await within(dialog).findByText(errors.tooLarge)).toBeInTheDocument();

    await user.click(within(dialog).getByRole("button", { name: actions.import }));
    expect(await within(dialog).findByText(errors.fileRequired)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("shows the server's JUnit errors in the dialog", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, { [IMPORT_PATH]: createErrorResult(422, "JUNIT_NO_MAPPED_TESTS") });
    renderButton();

    const dialog = await openDialog(user);
    await within(dialog).findByText(form.description);
    await chooseFile(user, dialog, JUNIT_FILE);
    await user.click(within(dialog).getByRole("button", { name: actions.import }));

    expect(
      await within(dialog).findByText(englishErrors.api.JUNIT_NO_MAPPED_TESTS),
    ).toBeInTheDocument();

    respondWithRoutes(apiPost, { [IMPORT_PATH]: createErrorResult(422, "JUNIT_INVALID") });
    await user.click(within(dialog).getByRole("button", { name: actions.import }));
    expect(await within(dialog).findByText(englishErrors.api.JUNIT_INVALID)).toBeInTheDocument();
  });

  it("explains that a project without an active environment cannot import", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, {
      [ENVIRONMENTS_PATH]: createSuccessResult([]),
      [SUITES_PATH]: createSuccessResult([]),
    });
    renderButton();

    const dialog = await openDialog(user);

    expect(await within(dialog).findByText(form.noEnvironment)).toBeInTheDocument();
    await waitFor(() => {
      expect(within(dialog).getByRole("button", { name: actions.import })).toBeDisabled();
    });
  });
});
