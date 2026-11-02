import type { Project } from "@/components/project-context/typing/types/project.type";
import englishCaseReview from "@/lib/i18n/locales/en/caseReview.json";
import englishProjects from "@/lib/i18n/locales/en/projects.json";
import { apiPatch } from "@/modules/test-cases/test/mocks/api-client.mock";
import {
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "@/modules/test-cases/test/utils/api-result.util";
import { buildProject } from "@/modules/test-cases/test/utils/project-fixture.util";
import { renderWithProject } from "@/modules/test-cases/test/utils/render-with-project.util";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { ReviewSettingsCard } from "./review-settings-card";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("@/modules/test-cases/test/mocks/api-client.mock")).apiClientMock;
});

const PROJECT_PATH = "/api/projects/{project_key}";

const { settings } = englishCaseReview;

const PROJECT = buildProject({ myRole: "admin" });

describe("ReviewSettingsCard", () => {
  beforeEach(() => {
    apiPatch.mockReset();
    respondWithRoutes(apiPatch, {
      [PROJECT_PATH]: (): ApiResult => {
        const body = (apiPatch.mock.calls.at(-1)?.[1] as { body: Partial<Project> }).body;
        return createSuccessResult({ ...PROJECT, ...body });
      },
    });
  });

  it("starts off and saves the rule only when it changed", async () => {
    const user = userEvent.setup();
    const { container } = renderWithProject(<ReviewSettingsCard project={PROJECT} />, PROJECT);

    const toggle = screen.getByRole("switch", {
      name: new RegExp(`^${settings.separateReviewer}`),
    });
    const save = screen.getByRole("button", { name: englishProjects.settings.save });
    expect(screen.getByRole("heading", { name: settings.title })).toBeInTheDocument();
    expect(toggle).not.toBeChecked();
    expect(save).toBeDisabled();
    expect(await axe(container)).toHaveNoViolations();

    await user.click(toggle);
    expect(save).toBeEnabled();
    await user.click(save);

    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledWith(PROJECT_PATH, {
        params: { path: { project_key: "SHOP" } },
        body: { requireSeparateReviewer: true },
      });
    });
    expect(await screen.findByText(settings.saved)).toBeInTheDocument();
  });

  it("shows the saved value and follows a newer project from the server", async () => {
    const { rerenderWithProject } = renderWithProject(
      <ReviewSettingsCard project={buildProject({ requireSeparateReviewer: true })} />,
      PROJECT,
    );

    expect(
      screen.getByRole("switch", { name: new RegExp(`^${settings.separateReviewer}`) }),
    ).toBeChecked();

    rerenderWithProject(
      <ReviewSettingsCard project={buildProject({ requireSeparateReviewer: false })} />,
    );

    await waitFor(() => {
      expect(
        screen.getByRole("switch", { name: new RegExp(`^${settings.separateReviewer}`) }),
      ).not.toBeChecked();
    });
    expect(screen.getByRole("button", { name: englishProjects.settings.save })).toBeDisabled();
  });
});
