import englishEnvironments from "@/lib/i18n/locales/en/environments.json";
import englishTestData from "@/lib/i18n/locales/en/testData.json";
import { act, screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { TestDataPage } from "./test-data";
import { apiDelete, apiGet, apiPost, apiPut } from "./test/mocks/api-client.mock";
import { routerReplace } from "./test/mocks/next-navigation.mock";
import {
  createCreatedResult,
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "./test/utils/api-result.util";
import {
  ADMIN_CAPABILITIES,
  buildProject,
  DEV_CAPABILITIES,
  QC_CAPABILITIES,
  VIEWER_CAPABILITIES,
} from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import {
  buildUploadedFile,
  IMPORT_FILE_ID,
  resetUpload,
  uploadFile,
} from "./test/utils/signed-upload-stub.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import {
  buildDataItem,
  buildEnvironment,
  LEGACY_ENVIRONMENT_ID,
  STAGING_ENVIRONMENT_ID,
} from "./test/utils/test-data-fixture.util";
import { SECRET_REVEAL_DURATION_IN_MILLISECONDS } from "./typing/constants/test-data.constant";
import { TestDataTab } from "./typing/enums/test-data-tab.enum";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

vi.mock("@/lib/uploads/hooks/use-signed-upload", async () => {
  return (await import("./test/utils/signed-upload-stub.util")).signedUploadMock;
});

const TEST_DATA_PATH = "/api/projects/{project_key}/test-data";
const ENVIRONMENTS_PATH = "/api/projects/{project_key}/environments";
const REVEAL_PATH = "/api/projects/{project_key}/test-data/{item_id}/reveal";
const PREVIEW_PATH = "/api/projects/{project_key}/test-data/import/preview";
const COMMIT_PATH = "/api/projects/{project_key}/test-data/import/commit";

const { actions, grid, secret, form, toasts } = englishTestData;

const staging = buildEnvironment();
const legacy = buildEnvironment({
  id: LEGACY_ENVIRONMENT_ID,
  name: "Legacy",
  isArchived: true,
  archivedAt: "2026-10-02T09:00:00Z",
});

const projectBasePath = buildDataItem({ id: "a1000000-0000-4000-8000-000000000001" });
const stagingBasePath = buildDataItem({
  id: "a1000000-0000-4000-8000-000000000002",
  environmentId: STAGING_ENVIRONMENT_ID,
  value: "/staging-shop",
});
const apiUrl = buildDataItem({
  id: "a1000000-0000-4000-8000-000000000003",
  key: "API_URL",
  kind: "variable",
  value: "https://api.example.test",
});
const password = buildDataItem({
  id: "a1000000-0000-4000-8000-000000000004",
  key: "PASSWORD",
  kind: "secret",
  value: null,
});
const legacyToken = buildDataItem({
  id: "a1000000-0000-4000-8000-000000000005",
  key: "LEGACY_TOKEN",
  environmentId: LEGACY_ENVIRONMENT_ID,
  value: "old",
});

const label = (template: string, values: Record<string, string>): string => {
  return Object.entries(values).reduce((text, [name, value]) => {
    return text.replace(`{{${name}}}`, value);
  }, template);
};

const findRow = async (key: string): Promise<HTMLElement> => {
  const header = await screen.findByRole("rowheader", { name: new RegExp(`^${key}`) });
  const row = header.closest("tr");
  if (row === null) {
    throw new Error(`No row for ${key}`);
  }

  return row;
};

const findCells = async (key: string): Promise<HTMLElement[]> => {
  return within(await findRow(key)).getAllByRole("cell");
};

const renderPage = (
  capabilities = VIEWER_CAPABILITIES,
  initialTab = TestDataTab.DATA,
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(
    <TestDataPage initialTab={initialTab} />,
    buildProject({ capabilities }),
  );
};

const openAddModal = async (user: UserEvent): Promise<HTMLElement> => {
  await user.click(await screen.findByRole("button", { name: actions.add }));

  return screen.findByRole("dialog");
};

describe("TestDataPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    apiPut.mockReset();
    apiDelete.mockReset();
    uploadFile.mockReset();
    resetUpload.mockReset();
    respondWithRoutes(apiGet, {
      [TEST_DATA_PATH]: createSuccessResult([
        projectBasePath,
        stagingBasePath,
        apiUrl,
        password,
        legacyToken,
      ]),
      [ENVIRONMENTS_PATH]: createSuccessResult([legacy, staging]),
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("shows a read-only grid to viewers with masked secrets", async () => {
    renderPage();

    const passwordCells = await findCells("PASSWORD");
    expect(within(passwordCells[0] as HTMLElement).getByText(secret.mask)).toBeInTheDocument();
    expect(
      within(passwordCells[0] as HTMLElement).getByText(secret.revealOnlyRoles),
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^Reveal/ })).toBeNull();
    expect(screen.queryByRole("button", { name: actions.add })).toBeNull();
    expect(screen.queryByRole("button", { name: actions.import })).toBeNull();
    expect(screen.queryByRole("button", { name: /^Edit / })).toBeNull();
    expect(screen.queryByRole("button", { name: /^Delete / })).toBeNull();
    expect(screen.queryByRole("button", { name: /^Override / })).toBeNull();
  });

  it("shows overrides, inherited values and archived columns on demand", async () => {
    const user = userEvent.setup();
    renderPage();

    const basePathCells = await findCells("BASE_PATH");
    expect(basePathCells).toHaveLength(2);
    expect(within(basePathCells[0] as HTMLElement).getByText("/shop")).toBeInTheDocument();
    expect(within(basePathCells[1] as HTMLElement).getByText("/staging-shop")).toBeInTheDocument();
    const apiUrlCells = await findCells("API_URL");
    expect(within(apiUrlCells[0] as HTMLElement).getByRole("link")).toHaveAttribute(
      "href",
      "https://api.example.test",
    );
    expect(within(apiUrlCells[1] as HTMLElement).getByText(grid.inherited)).toBeInTheDocument();
    expect(screen.getAllByRole("columnheader").map((header) => header.textContent)).toEqual([
      grid.key,
      grid.allEnvironments,
      "Staging",
    ]);

    await user.click(screen.getByRole("switch", { name: grid.showArchived }));

    expect(screen.getAllByRole("columnheader").map((header) => header.textContent)).toEqual([
      grid.key,
      grid.allEnvironments,
      "Staging",
      `Legacy${grid.archived}`,
    ]);
    const legacyCells = await findCells("LEGACY_TOKEN");
    expect(within(legacyCells[2] as HTMLElement).getByText("old")).toBeInTheDocument();
  });

  it("filters the keys and reports when nothing matches", async () => {
    const user = userEvent.setup();
    renderPage();

    await findRow("PASSWORD");
    await user.type(screen.getByRole("textbox", { name: grid.search }), "pass");

    expect(screen.getAllByRole("rowheader")).toHaveLength(1);
    await user.type(screen.getByRole("textbox", { name: grid.search }), "zzz");
    expect(await screen.findByText(grid.noMatch)).toBeInTheDocument();
  });

  it("lets QC reveal a secret and hides it again after 30 seconds", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    respondWithRoutes(apiPost, { [REVEAL_PATH]: createSuccessResult({ value: "s3cret" }) });
    const { queryClient } = renderPage(QC_CAPABILITIES);

    await user.click(
      await screen.findByRole("button", { name: label(secret.revealLabel, { key: "PASSWORD" }) }),
    );

    expect(await screen.findByText("s3cret")).toBeInTheDocument();
    expect(apiPost).toHaveBeenCalledWith(REVEAL_PATH, {
      params: { path: { project_key: "SHOP", item_id: password.id } },
    });
    expect(screen.getByRole("button", { name: "Copy" })).toBeInTheDocument();
    expect(JSON.stringify(queryClient.getQueryCache().getAll())).not.toContain("s3cret");

    act(() => {
      vi.advanceTimersByTime(SECRET_REVEAL_DURATION_IN_MILLISECONDS);
    });

    expect(screen.queryByText("s3cret")).toBeNull();
    expect(
      screen.getByRole("button", { name: label(secret.revealLabel, { key: "PASSWORD" }) }),
    ).toBeInTheDocument();
  });

  it("lets a dev edit variables but not secrets", async () => {
    const user = userEvent.setup();
    renderPage(DEV_CAPABILITIES);

    expect(
      await screen.findByRole("button", {
        name: label(actions.edit, { key: "BASE_PATH", scope: grid.allEnvironments }),
      }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", {
        name: label(actions.edit, { key: "PASSWORD", scope: grid.allEnvironments }),
      }),
    ).toBeNull();

    expect(
      screen.getByRole("button", {
        name: label(actions.override, { key: "API_URL", scope: "Staging" }),
      }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", {
        name: label(actions.override, { key: "PASSWORD", scope: "Staging" }),
      }),
    ).toBeNull();

    await openAddModal(user);
    expect(screen.getByRole("checkbox", { name: form.secret })).toBeDisabled();
    expect(screen.getByText(form.secretLocked)).toBeInTheDocument();
  });

  it("edits a variable with its value prefilled", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPut, {
      "/api/projects/{project_key}/test-data/{item_id}": createSuccessResult(projectBasePath),
    });
    renderPage(DEV_CAPABILITIES);

    await user.click(
      await screen.findByRole("button", {
        name: label(actions.edit, { key: "BASE_PATH", scope: grid.allEnvironments }),
      }),
    );
    const valueInput = screen.getByRole("textbox", { name: /^Value/ });
    expect(valueInput).toHaveValue("/shop");
    await user.clear(valueInput);
    await user.type(valueInput, "/store");
    await user.click(screen.getByRole("button", { name: actions.save }));

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith("/api/projects/{project_key}/test-data/{item_id}", {
        params: { path: { project_key: "SHOP", item_id: projectBasePath.id } },
        body: { key: "BASE_PATH", kind: "variable", value: "/store", description: "" },
      });
    });
    expect(await screen.findByText(toasts.updated)).toBeInTheDocument();
  });

  it("keeps a secret value when the field is left empty", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPut, {
      "/api/projects/{project_key}/test-data/{item_id}": createSuccessResult(password),
    });
    renderPage(QC_CAPABILITIES);

    await user.click(
      await screen.findByRole("button", {
        name: label(actions.edit, { key: "PASSWORD", scope: grid.allEnvironments }),
      }),
    );
    const dialog = await screen.findByRole("dialog");
    expect(within(dialog).getByText(form.keepSecretHint)).toBeInTheDocument();
    expect(within(dialog).getByLabelText(new RegExp(`^${form.secretValue}`))).toHaveValue("");
    await user.click(within(dialog).getByRole("button", { name: actions.save }));

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith("/api/projects/{project_key}/test-data/{item_id}", {
        params: { path: { project_key: "SHOP", item_id: password.id } },
        body: { key: "PASSWORD", kind: "secret", value: null, description: "" },
      });
    });
  });

  it("creates an item with the right body", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [TEST_DATA_PATH]: createCreatedResult(buildDataItem({ key: "NEW_KEY" })),
    });
    renderPage(ADMIN_CAPABILITIES);

    const dialog = await openAddModal(user);
    await user.type(within(dialog).getByRole("textbox", { name: /^Key/ }), " NEW_KEY ");
    await user.type(within(dialog).getByRole("textbox", { name: /^Value/ }), "hello");
    await user.click(within(dialog).getByRole("button", { name: actions.create }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(TEST_DATA_PATH, {
        params: { path: { project_key: "SHOP" } },
        body: {
          key: "NEW_KEY",
          kind: "variable",
          value: "hello",
          environmentId: null,
          description: null,
        },
      });
    });
    expect(await screen.findByText(toasts.created)).toBeInTheDocument();
  });

  it("validates the key and the value before creating", async () => {
    const user = userEvent.setup();
    renderPage(ADMIN_CAPABILITIES);

    const dialog = await openAddModal(user);
    await user.type(within(dialog).getByRole("textbox", { name: /^Key/ }), "1bad key");
    await user.click(within(dialog).getByRole("button", { name: actions.create }));

    expect(await within(dialog).findByText(form.keyInvalid)).toBeInTheDocument();
    expect(within(dialog).getByText(form.valueRequired)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("shows a taken key on the key field", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [TEST_DATA_PATH]: createErrorResult(409, "TEST_DATA_KEY_ALREADY_USED"),
    });
    renderPage(ADMIN_CAPABILITIES);

    const dialog = await openAddModal(user);
    await user.type(within(dialog).getByRole("textbox", { name: /^Key/ }), "BASE_PATH");
    await user.type(within(dialog).getByRole("textbox", { name: /^Value/ }), "/again");
    await user.click(within(dialog).getByRole("button", { name: actions.create }));

    expect(
      await within(dialog).findByText(englishTestData.errors.keyAlreadyUsed),
    ).toBeInTheDocument();
  });

  it("overrides an inherited value in an environment", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, { [TEST_DATA_PATH]: createCreatedResult(apiUrl) });
    renderPage(ADMIN_CAPABILITIES);

    await user.click(
      await screen.findByRole("button", {
        name: label(actions.override, { key: "API_URL", scope: "Staging" }),
      }),
    );
    const dialog = await screen.findByRole("dialog");
    expect(within(dialog).getByRole("textbox", { name: /^Key/ })).toBeDisabled();
    await user.type(
      within(dialog).getByRole("textbox", { name: /^Value/ }),
      "https://staging-api.example.test",
    );
    await user.click(within(dialog).getByRole("button", { name: actions.create }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(TEST_DATA_PATH, {
        params: { path: { project_key: "SHOP" } },
        body: {
          key: "API_URL",
          kind: "variable",
          value: "https://staging-api.example.test",
          environmentId: STAGING_ENVIRONMENT_ID,
          description: null,
        },
      });
    });
  });

  it("deletes an item after confirmation", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiDelete, {
      "/api/projects/{project_key}/test-data/{item_id}": {
        response: new Response(null, { status: 204 }),
      },
    });
    renderPage(ADMIN_CAPABILITIES);

    await user.click(
      await screen.findByRole("button", {
        name: label(actions.deleteItem, { key: "BASE_PATH", scope: "Staging" }),
      }),
    );
    const dialog = await screen.findByRole("dialog");
    expect(
      within(dialog).getByText(
        label(englishTestData.delete.message, { key: "BASE_PATH", scope: "Staging" }),
      ),
    ).toBeInTheDocument();
    await user.click(within(dialog).getByRole("button", { name: actions.delete }));

    await waitFor(() => {
      expect(apiDelete).toHaveBeenCalledWith("/api/projects/{project_key}/test-data/{item_id}", {
        params: { path: { project_key: "SHOP", item_id: stagingBasePath.id } },
      });
    });
    expect(await screen.findByText(toasts.deleted)).toBeInTheDocument();
  });

  it("imports the chosen rows of a previewed file", async () => {
    const user = userEvent.setup();
    uploadFile.mockImplementation((file) => Promise.resolve(buildUploadedFile(file)));
    respondWithRoutes(apiPost, {
      [PREVIEW_PATH]: createSuccessResult({
        format: "dotenv",
        items: [
          { key: "NEW_KEY", kind: "variable", value: "1", action: "create" },
          { key: "BASE_PATH", kind: "variable", value: "/shop", action: "unchanged" },
          { key: "API_TOKEN", kind: "secret", value: null, action: "update" },
        ],
        skipped: [{ location: "line 4", reason: "invalid_line" }],
      }),
      [COMMIT_PATH]: createSuccessResult({ created: 1, updated: 1, unchanged: 0 }),
    });
    renderPage(ADMIN_CAPABILITIES);

    await user.click(await screen.findByRole("button", { name: actions.import }));
    const dialog = await screen.findByRole("dialog");
    const input = dialog.querySelector<HTMLInputElement>('input[type="file"]');
    expect(input).not.toBeNull();
    await user.upload(input as HTMLInputElement, new File(["NEW_KEY=1"], ".env.staging"));

    const includeNewKey = await within(dialog).findByRole("checkbox", {
      name: label(englishTestData.import.includeKey, { key: "NEW_KEY" }),
    });
    const uploadedFile = uploadFile.mock.calls[0]?.[0];
    expect(uploadedFile?.type).toBe("text/plain");
    expect(apiPost).toHaveBeenCalledWith(PREVIEW_PATH, {
      params: { path: { project_key: "SHOP" } },
      body: { fileId: IMPORT_FILE_ID, environmentId: null },
    });
    expect(includeNewKey).toBeChecked();
    expect(
      within(dialog).getByRole("checkbox", {
        name: label(englishTestData.import.includeKey, { key: "BASE_PATH" }),
      }),
    ).not.toBeChecked();
    expect(
      within(dialog).getByRole("checkbox", {
        name: label(englishTestData.import.includeKey, { key: "API_TOKEN" }),
      }),
    ).toBeChecked();
    expect(
      within(dialog).getByText(englishTestData.import.skipReason.invalid_line),
    ).toBeInTheDocument();

    await user.click(within(dialog).getByRole("button", { name: actions.commit }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(COMMIT_PATH, {
        params: { path: { project_key: "SHOP" } },
        body: {
          fileId: IMPORT_FILE_ID,
          environmentId: null,
          items: [
            { key: "NEW_KEY", kind: "variable" },
            { key: "API_TOKEN", kind: "secret" },
          ],
        },
      });
    });
    expect(
      await screen.findByText(
        label(toasts.imported, { created: "1", updated: "1", unchanged: "0" }),
      ),
    ).toBeInTheDocument();
    expect(resetUpload).toHaveBeenCalled();
  });

  it("locks suggested secrets for a dev and rejects a wrong file locally", async () => {
    const user = userEvent.setup();
    uploadFile.mockImplementation((file) => Promise.resolve(buildUploadedFile(file)));
    respondWithRoutes(apiPost, {
      [PREVIEW_PATH]: createSuccessResult({
        format: "json",
        items: [{ key: "API_TOKEN", kind: "secret", value: null, action: "create" }],
        skipped: [],
      }),
    });
    renderPage(DEV_CAPABILITIES);

    await user.click(await screen.findByRole("button", { name: actions.import }));
    const dialog = await screen.findByRole("dialog");
    const input = dialog.querySelector<HTMLInputElement>('input[type="file"]') as HTMLInputElement;
    await user.upload(input, new File(["x"], "notes.txt"));

    expect(
      await within(dialog).findByText(englishTestData.import.errors.extension),
    ).toBeInTheDocument();
    expect(uploadFile).not.toHaveBeenCalled();

    await user.upload(input, new File(['{"API_TOKEN":"x"}'], "data.json"));

    const includeToken = await within(dialog).findByRole("checkbox", {
      name: label(englishTestData.import.includeKey, { key: "API_TOKEN" }),
    });
    expect(uploadFile.mock.calls[0]?.[0].type).toBe("application/json");
    expect(includeToken).not.toBeChecked();
    expect(includeToken).toBeDisabled();
    expect(within(dialog).getByText(englishTestData.import.secretLocked)).toBeInTheDocument();
    expect(within(dialog).getByRole("button", { name: actions.commit })).toBeDisabled();
  });

  it("explains a file type the project does not allow", async () => {
    const user = userEvent.setup();
    const { ApiError } = await import("@/lib/api/api-error");
    uploadFile.mockRejectedValue(
      new ApiError({ status: 422, code: "FILE_TYPE_NOT_ALLOWED", message: "not allowed" }),
    );
    renderPage(ADMIN_CAPABILITIES);

    await user.click(await screen.findByRole("button", { name: actions.import }));
    const dialog = await screen.findByRole("dialog");
    const input = dialog.querySelector<HTMLInputElement>('input[type="file"]') as HTMLInputElement;
    await user.upload(input, new File(["KEY=1"], ".env"));

    expect(
      await within(dialog).findByText(englishTestData.import.errors.typeNotAllowed),
    ).toBeInTheDocument();
  });

  it("shows an empty state with add and import for editors", async () => {
    respondWithRoutes(apiGet, {
      [TEST_DATA_PATH]: createSuccessResult([]),
      [ENVIRONMENTS_PATH]: createSuccessResult([]),
    });
    renderPage(DEV_CAPABILITIES);

    expect(await screen.findByText(englishTestData.empty.title)).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: actions.add })).toHaveLength(2);
    expect(screen.getAllByRole("button", { name: actions.import })).toHaveLength(2);
    expect(screen.getByText(grid.noEnvironmentsHint)).toBeInTheDocument();
  });

  it("retries after a load error", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, {
      [TEST_DATA_PATH]: createErrorResult(500, "CONFLICT"),
      [ENVIRONMENTS_PATH]: createSuccessResult([staging]),
    });
    renderPage();

    expect(await screen.findByText(englishTestData.errors.loadFailed)).toBeInTheDocument();
    respondWithRoutes(apiGet, {
      [TEST_DATA_PATH]: createSuccessResult([projectBasePath]),
      [ENVIRONMENTS_PATH]: createSuccessResult([staging]),
    });
    await user.click(screen.getByRole("button", { name: actions.retry }));

    expect(await findRow("BASE_PATH")).toBeInTheDocument();
  });

  it("warns inline when the environments cannot be loaded and retries them", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, {
      [TEST_DATA_PATH]: createSuccessResult([projectBasePath, stagingBasePath]),
      [ENVIRONMENTS_PATH]: createErrorResult(500, "CONFLICT"),
    });
    renderPage();

    expect(
      await screen.findByText(englishTestData.errors.environmentsLoadFailed),
    ).toBeInTheDocument();
    expect(screen.queryByText(grid.noEnvironmentsHint)).not.toBeInTheDocument();
    expect(screen.queryByRole("columnheader", { name: "Staging" })).not.toBeInTheDocument();
    respondWithRoutes(apiGet, {
      [TEST_DATA_PATH]: createSuccessResult([projectBasePath, stagingBasePath]),
      [ENVIRONMENTS_PATH]: createSuccessResult([staging]),
    });
    await user.click(screen.getByRole("button", { name: actions.retry }));

    expect(await screen.findByRole("columnheader", { name: "Staging" })).toBeInTheDocument();
    expect(
      screen.queryByText(englishTestData.errors.environmentsLoadFailed),
    ).not.toBeInTheDocument();
    expect(
      apiGet.mock.calls.filter(([path]) => {
        return path === ENVIRONMENTS_PATH;
      }),
    ).toHaveLength(2);
  });

  it("opens the environments tab from the URL and keeps the tab in the URL", async () => {
    const user = userEvent.setup();
    renderPage(VIEWER_CAPABILITIES, TestDataTab.ENVIRONMENTS);

    expect(
      await screen.findByRole("tab", { name: englishTestData.tabs.environments, selected: true }),
    ).toBeInTheDocument();
    expect(await screen.findByText(englishEnvironments.showArchived)).toBeInTheDocument();

    await user.click(screen.getByRole("tab", { name: englishTestData.tabs.data }));

    expect(routerReplace).toHaveBeenCalledWith("?tab=data", { scroll: false });
    expect(await findRow("BASE_PATH")).toBeInTheDocument();
  });

  it("has no accessibility violations", async () => {
    const { container } = renderPage(ADMIN_CAPABILITIES);

    await findRow("PASSWORD");
    expect(await axe(container)).toHaveNoViolations();
  });
});
