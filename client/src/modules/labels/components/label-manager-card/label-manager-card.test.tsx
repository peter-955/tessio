import englishLabels from "@/lib/i18n/locales/en/labels.json";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiDelete, apiGet, apiPatch, apiPost } from "../../test/mocks/api-client.mock";
import {
  createCreatedResult,
  createErrorResult,
  createNoContentResult,
  createSuccessResult,
  respondWithRoutes,
} from "../../test/utils/api-result.util";
import { buildLabel, CHECKOUT_LABEL_ID } from "../../test/utils/label-fixture.util";
import { ADMIN_CAPABILITIES, buildProject } from "../../test/utils/project-fixture.util";
import { renderWithProject } from "../../test/utils/render-with-project.util";
import { openSelectOption } from "../../test/utils/select-option.util";
import { stubScrollIntoView } from "../../test/utils/stub-scroll-into-view.util";
import { LabelManagerCard } from "./label-manager-card";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

const LABELS_PATH = "/api/projects/{project_key}/labels";
const LABEL_PATH = "/api/projects/{project_key}/labels/{label_id}";

const smoke = buildLabel();
const checkout = buildLabel({
  id: CHECKOUT_LABEL_ID,
  name: "checkout",
  color: "blue",
  caseCount: 1,
});
const adminProject = buildProject({ myRole: "admin", capabilities: ADMIN_CAPABILITIES });

const renderCard = (canManage = true): ReturnType<typeof renderWithProject> => {
  return renderWithProject(
    <LabelManagerCard projectKey="SHOP" canManage={canManage} />,
    adminProject,
  );
};

const openRowMenu = async (user: UserEvent, name: string): Promise<void> => {
  await user.click(
    await screen.findByRole("button", {
      name: englishLabels.manager.actionsFor.replace("{{name}}", name),
    }),
  );
};

const findDialog = async (): Promise<HTMLElement> => {
  return screen.findByRole("dialog");
};

describe("LabelManagerCard", () => {
  beforeAll(() => {
    stubScrollIntoView();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    apiPatch.mockReset();
    apiDelete.mockReset();
    respondWithRoutes(apiGet, { [LABELS_PATH]: createSuccessResult([checkout, smoke]) });
  });

  it("lists the labels with how many cases use them", async () => {
    const { container } = renderCard();

    const table = await screen.findByRole("table", { name: englishLabels.manager.tableLabel });
    const rows = within(table).getAllByRole("row");
    expect(rows).toHaveLength(3);
    expect(within(rows[1]).getByText("checkout")).toBeInTheDocument();
    expect(within(rows[1]).getByText("Used by 1 case")).toBeInTheDocument();
    expect(within(rows[2]).getByText("Used by 3 cases")).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("says when the project has no labels", async () => {
    respondWithRoutes(apiGet, { [LABELS_PATH]: createSuccessResult([]) });
    renderCard();

    expect(await screen.findByText(englishLabels.manager.empty)).toBeInTheDocument();
  });

  it("shows the list without actions when the viewer cannot manage labels", async () => {
    renderCard(false);

    expect(await screen.findByText("checkout")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: englishLabels.manager.add })).toBeNull();
    expect(
      screen.queryByRole("button", {
        name: englishLabels.manager.actionsFor.replace("{{name}}", "checkout"),
      }),
    ).toBeNull();
  });

  it("creates a label with a name and a colour", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [LABELS_PATH]: createCreatedResult(buildLabel({ name: "regression", color: "violet" })),
    });
    renderCard();

    await user.click(await screen.findByRole("button", { name: englishLabels.manager.add }));
    const dialog = await findDialog();
    await user.type(within(dialog).getByRole("textbox", { name: /^Name/ }), " regression ");
    await user.click(await openSelectOption(user, /^Color/, englishLabels.colors.violet));
    await user.click(within(dialog).getByRole("button", { name: englishLabels.form.create }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(LABELS_PATH, {
        params: { path: { project_key: "SHOP" } },
        body: { name: "regression", color: "violet" },
      });
    });
    expect(await screen.findByText(englishLabels.toasts.created)).toBeInTheDocument();
  });

  it("refuses a name another label already uses, without regard to case", async () => {
    const user = userEvent.setup();
    renderCard();

    await user.click(await screen.findByRole("button", { name: englishLabels.manager.add }));
    const dialog = await findDialog();
    await user.type(within(dialog).getByRole("textbox", { name: /^Name/ }), "SMOKE");
    await user.click(within(dialog).getByRole("button", { name: englishLabels.form.create }));

    expect(
      await within(dialog).findByText(englishLabels.validation.alreadyUsed),
    ).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("shows the server's name conflict on the name field", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, { [LABELS_PATH]: createErrorResult(409, "CONFLICT") });
    renderCard();

    await user.click(await screen.findByRole("button", { name: englishLabels.manager.add }));
    const dialog = await findDialog();
    await user.type(within(dialog).getByRole("textbox", { name: /^Name/ }), "Fresh");
    await user.click(within(dialog).getByRole("button", { name: englishLabels.form.create }));

    expect(await within(dialog).findByText(englishLabels.errors.nameAlreadyUsed)).toBeVisible();
  });

  it("renames a label and sends only the changed field", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPatch, {
      [LABEL_PATH]: createSuccessResult({ ...checkout, name: "Checkout" }),
    });
    renderCard();

    await openRowMenu(user, "checkout");
    await user.click(await screen.findByRole("menuitem", { name: englishLabels.manager.edit }));
    const dialog = await findDialog();
    const nameInput = within(dialog).getByRole("textbox", { name: /^Name/ });
    await user.clear(nameInput);
    await user.type(nameInput, "Checkout");
    await user.click(within(dialog).getByRole("button", { name: englishLabels.form.save }));

    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledWith(LABEL_PATH, {
        params: { path: { project_key: "SHOP", label_id: checkout.id } },
        body: { name: "Checkout" },
      });
    });
    expect(await screen.findByText(englishLabels.toasts.updated)).toBeInTheDocument();
  });

  it("asks before deleting and names how many cases lose the label", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiDelete, { [LABEL_PATH]: createNoContentResult() });
    renderCard();

    await openRowMenu(user, "smoke");
    await user.click(await screen.findByRole("menuitem", { name: englishLabels.manager.delete }));
    const dialog = await findDialog();
    expect(
      within(dialog).getByText("Delete smoke? It is removed from 3 cases."),
    ).toBeInTheDocument();
    await user.click(within(dialog).getByRole("button", { name: englishLabels.delete.confirm }));

    await waitFor(() => {
      expect(apiDelete).toHaveBeenCalledWith(LABEL_PATH, {
        params: { path: { project_key: "SHOP", label_id: smoke.id } },
      });
    });
    expect(await screen.findByText(englishLabels.toasts.deleted)).toBeInTheDocument();
  });
});
