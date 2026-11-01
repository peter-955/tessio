import englishEnvironments from "@/lib/i18n/locales/en/environments.json";
import { GET_ENVIRONMENTS_KEY } from "@/shared/hooks/queries/use-get-environments";
import { GET_PROJECT_KEY } from "@/shared/hooks/queries/use-get-project";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { EnvironmentsPanel } from "./environments";
import { apiDelete, apiGet, apiPost, apiPut } from "./test/mocks/api-client.mock";
import {
  createCreatedResult,
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "./test/utils/api-result.util";
import { buildEnvironment } from "./test/utils/environment-fixture.util";
import {
  ADMIN_CAPABILITIES,
  buildProject,
  VIEWER_CAPABILITIES,
} from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

const ENVIRONMENTS_PATH = "/api/projects/{project_key}/environments";
const ENVIRONMENT_PATH = "/api/projects/{project_key}/environments/{environment_id}";
const ARCHIVE_PATH = "/api/projects/{project_key}/environments/{environment_id}/archive";

const staging = buildEnvironment();
const production = buildEnvironment({
  id: "2c8e2a1f-6b54-4d66-8e1c-1d3c7b1f5a22",
  name: "Production",
  baseUrl: "https://shop.example.test",
  healthCheckUrl: null,
});
const legacy = buildEnvironment({
  id: "3d9f3b2a-7c65-4e77-9f2d-2e4d8c2a6b33",
  name: "Legacy",
  baseUrl: "https://legacy.example.test",
  healthCheckUrl: null,
  isArchived: true,
  archivedAt: "2026-10-02T09:00:00Z",
});

const adminProject = buildProject({
  capabilities: ADMIN_CAPABILITIES,
  myRole: "admin",
  defaultEnvironmentId: production.id,
});

const findRow = async (name: string): Promise<HTMLElement> => {
  const cell = await screen.findByText(name);
  const row = cell.closest("tr");
  if (row === null) {
    throw new Error(`No row for ${name}`);
  }

  return row;
};

const openRowMenu = async (user: UserEvent, name: string): Promise<void> => {
  await user.click(
    await screen.findByRole("button", {
      name: englishEnvironments.table.actionsFor.replace("{{name}}", name),
    }),
  );
};

const openCreateModal = async (user: UserEvent): Promise<void> => {
  await user.click(await screen.findByRole("button", { name: englishEnvironments.actions.add }));
};

const fillCreateForm = async (user: UserEvent, name: string, baseUrl: string): Promise<void> => {
  await user.type(screen.getByRole("textbox", { name: /^Name/ }), name);
  await user.type(screen.getByRole("textbox", { name: /^Base URL/ }), baseUrl);
};

describe("EnvironmentsPanel", () => {
  beforeAll(() => {
    stubScrollIntoView();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    apiPut.mockReset();
    apiDelete.mockReset();
    respondWithRoutes(apiGet, {
      [ENVIRONMENTS_PATH]: createSuccessResult([production, staging]),
    });
  });

  it("lists the environments with the default and archived badges", async () => {
    const user = userEvent.setup();
    apiGet.mockImplementation((_path, options) => {
      const query = (options as { params: { query: { includeArchived: boolean } } }).params.query;

      return Promise.resolve(
        createSuccessResult(
          query.includeArchived ? [legacy, production, staging] : [production, staging],
        ),
      );
    });
    renderWithProject(<EnvironmentsPanel />, adminProject);

    const productionRow = await findRow("Production");
    expect(within(productionRow).getByText(englishEnvironments.table.default)).toBeInTheDocument();
    expect(within(productionRow).getByText(englishEnvironments.status.active)).toBeInTheDocument();
    expect(within(productionRow).getByRole("link", { name: production.baseUrl })).toHaveAttribute(
      "target",
      "_blank",
    );
    const stagingRow = await findRow("Staging");
    expect(within(stagingRow).queryByText(englishEnvironments.table.default)).toBeNull();
    expect(
      within(stagingRow).getByRole("link", { name: "https://staging.example.test/health" }),
    ).toHaveAttribute("rel", "noopener noreferrer");
    expect(screen.queryByText("Legacy")).toBeNull();

    await user.click(screen.getByRole("switch", { name: englishEnvironments.showArchived }));

    const legacyRow = await findRow("Legacy");
    expect(within(legacyRow).getByText(englishEnvironments.status.archived)).toBeInTheDocument();
    expect(apiGet).toHaveBeenLastCalledWith(ENVIRONMENTS_PATH, {
      params: { path: { project_key: "SHOP" }, query: { includeArchived: true } },
    });
  });

  it("validates the URL before creating an environment", async () => {
    const user = userEvent.setup();
    renderWithProject(<EnvironmentsPanel />, adminProject);

    await openCreateModal(user);
    await fillCreateForm(user, "QA", "qa.example.test");
    await user.click(screen.getByRole("button", { name: englishEnvironments.actions.create }));

    expect(await screen.findByText(englishEnvironments.form.urlInvalid)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("creates an environment with trimmed values and a null health check", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [ENVIRONMENTS_PATH]: createCreatedResult(buildEnvironment({ name: "QA" })),
    });
    renderWithProject(<EnvironmentsPanel />, adminProject);

    await openCreateModal(user);
    await fillCreateForm(user, "  QA ", "https://qa.example.test");
    await user.click(screen.getByRole("button", { name: englishEnvironments.actions.create }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(ENVIRONMENTS_PATH, {
        params: { path: { project_key: "SHOP" } },
        body: { name: "QA", baseUrl: "https://qa.example.test", healthCheckUrl: null },
      });
    });
    expect(await screen.findByText(englishEnvironments.toasts.created)).toBeInTheDocument();
  });

  it("shows a taken name on the name field", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [ENVIRONMENTS_PATH]: createErrorResult(409, "ENVIRONMENT_NAME_ALREADY_USED"),
    });
    renderWithProject(<EnvironmentsPanel />, adminProject);

    await openCreateModal(user);
    await fillCreateForm(user, "staging", "https://staging2.example.test");
    await user.click(screen.getByRole("button", { name: englishEnvironments.actions.create }));

    const nameInput = screen.getByRole("textbox", { name: /^Name/ });
    await waitFor(() => {
      expect(nameInput).toHaveAccessibleDescription(englishEnvironments.errors.nameAlreadyUsed);
    });
  });

  it("edits an environment", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPut, { [ENVIRONMENT_PATH]: createSuccessResult(staging) });
    renderWithProject(<EnvironmentsPanel />, adminProject);

    await openRowMenu(user, "Staging");
    await user.click(
      await screen.findByRole("menuitem", { name: englishEnvironments.actions.edit }),
    );
    const nameInput = screen.getByRole("textbox", { name: /^Name/ });
    expect(nameInput).toHaveValue("Staging");
    await user.clear(nameInput);
    await user.type(nameInput, "Staging EU");
    await user.click(screen.getByRole("button", { name: englishEnvironments.actions.save }));

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith(ENVIRONMENT_PATH, {
        params: { path: { project_key: "SHOP", environment_id: staging.id } },
        body: {
          name: "Staging EU",
          baseUrl: staging.baseUrl,
          healthCheckUrl: staging.healthCheckUrl,
        },
      });
    });
  });

  it("archives an environment and refreshes the list and the project", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [ARCHIVE_PATH]: createSuccessResult({ ...staging, isArchived: true }),
    });
    const { queryClient } = renderWithProject(<EnvironmentsPanel />, adminProject);
    const invalidateQueries = vi.spyOn(queryClient, "invalidateQueries");

    await openRowMenu(user, "Staging");
    await user.click(
      await screen.findByRole("menuitem", { name: englishEnvironments.actions.archive }),
    );

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(ARCHIVE_PATH, {
        params: { path: { project_key: "SHOP", environment_id: staging.id } },
      });
    });
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: [GET_ENVIRONMENTS_KEY] });
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: [GET_PROJECT_KEY] });
    expect(await screen.findByText(englishEnvironments.toasts.archived)).toBeInTheDocument();
  });

  it("offers only unarchive and delete for an archived environment", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, { [ENVIRONMENTS_PATH]: createSuccessResult([legacy]) });
    renderWithProject(<EnvironmentsPanel />, adminProject);

    await openRowMenu(user, "Legacy");

    const menuItems = await screen.findAllByRole("menuitem");
    expect(menuItems.map((menuItem) => menuItem.textContent)).toEqual([
      englishEnvironments.actions.unarchive,
      englishEnvironments.actions.delete,
    ]);
  });

  it("explains that a used environment cannot be deleted", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiDelete, {
      [ENVIRONMENT_PATH]: createErrorResult(409, "ENVIRONMENT_IN_USE"),
    });
    renderWithProject(<EnvironmentsPanel />, adminProject);

    await openRowMenu(user, "Staging");
    await user.click(
      await screen.findByRole("menuitem", { name: englishEnvironments.actions.delete }),
    );
    const dialog = await screen.findByRole("dialog");
    expect(
      within(dialog).getByText(englishEnvironments.delete.message.replace("{{name}}", "Staging")),
    ).toBeInTheDocument();
    await user.click(
      within(dialog).getByRole("button", { name: englishEnvironments.actions.delete }),
    );

    expect(await within(dialog).findByText(englishEnvironments.errors.inUse)).toBeInTheDocument();
    expect(apiDelete).toHaveBeenCalledWith(ENVIRONMENT_PATH, {
      params: { path: { project_key: "SHOP", environment_id: staging.id } },
    });
  });

  it("hides every write action from non-managers", async () => {
    renderWithProject(
      <EnvironmentsPanel />,
      buildProject({ capabilities: VIEWER_CAPABILITIES, defaultEnvironmentId: production.id }),
    );

    expect(await screen.findByText("Staging")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: englishEnvironments.actions.add })).toBeNull();
    expect(screen.queryByRole("button", { name: /^Actions for/ })).toBeNull();
  });

  it("shows an empty state with an add button for managers", async () => {
    respondWithRoutes(apiGet, { [ENVIRONMENTS_PATH]: createSuccessResult([]) });
    renderWithProject(<EnvironmentsPanel />, adminProject);

    expect(await screen.findByText(englishEnvironments.empty.title)).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: englishEnvironments.actions.add })).toHaveLength(
      2,
    );
  });

  it("retries after a load error", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, { [ENVIRONMENTS_PATH]: createErrorResult(500, "CONFLICT") });
    renderWithProject(<EnvironmentsPanel />, adminProject);

    expect(await screen.findByText(englishEnvironments.errors.loadFailed)).toBeInTheDocument();
    respondWithRoutes(apiGet, { [ENVIRONMENTS_PATH]: createSuccessResult([staging]) });
    await user.click(screen.getByRole("button", { name: englishEnvironments.actions.retry }));

    expect(await screen.findByText("Staging")).toBeInTheDocument();
  });

  it("has no accessibility violations", async () => {
    const { container } = renderWithProject(<EnvironmentsPanel />, adminProject);

    expect(await screen.findByText("Staging")).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });
});
