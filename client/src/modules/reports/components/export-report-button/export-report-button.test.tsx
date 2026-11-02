import englishReports from "@/lib/i18n/locales/en/reports.json";
import { act, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { GET_REPORT_LINK_KEY } from "../../hooks/queries/use-get-report-link";
import { apiGet, apiPost } from "../../test/mocks/api-client.mock";
import {
  createErrorResult,
  createSuccessResult,
  type ApiResult,
} from "../../test/utils/api-result.util";
import { buildProject, VIEWER_CAPABILITIES } from "../../test/utils/project-fixture.util";
import { renderWithProject } from "../../test/utils/render-with-project.util";
import type { ReportExportTarget } from "../../typing/types/report-export-target.type";
import { ExportReportButton } from "./export-report-button";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

const RUN_ID = "7a8b9c0d-1e2f-4a3b-8c4d-5e6f7a8b9c0d";
const PLAN_ID = "8b9c0d1e-2f3a-4b4c-9d5e-6f7a8b9c0d1e";
const FILE_ID = "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f";
const FILE_PATH = "/api/projects/{project_key}/files/{file_id}";
const DOWNLOAD_URL = "https://files.example.test/report.md";
const ACCEPTED_STATUS = 202;

const { modal, format, status } = englishReports;

const buildExport = (fileName: string): ApiResult => {
  return {
    data: {
      fileId: FILE_ID,
      fileName,
      format: "md",
      source: "run",
      sourceId: RUN_ID,
      sourceLabel: "SHOP-1",
    },
    response: new Response(null, { status: ACCEPTED_STATUS }),
  };
};

const renderButton = (
  target: ReportExportTarget,
  capabilities = VIEWER_CAPABILITIES,
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(<ExportReportButton target={target} />, buildProject({ capabilities }));
};

const exportAs = async (formatLabel: string): Promise<HTMLElement> => {
  const user = userEvent.setup();
  await user.click(screen.getByRole("button", { name: englishReports.button }));
  const dialog = await screen.findByRole("dialog");
  await user.click(within(dialog).getByRole("radio", { name: formatLabel }));
  await user.click(within(dialog).getByRole("button", { name: modal.export }));

  return dialog;
};

describe("ExportReportButton", () => {
  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    apiPost.mockResolvedValue(buildExport("run-SHOP-1-2026-11-01.md"));
  });

  it("is hidden without report.view", () => {
    renderButton(
      { source: "run", runId: RUN_ID },
      VIEWER_CAPABILITIES.filter((capability) => {
        return capability !== "report.view";
      }),
    );

    expect(screen.queryByRole("button", { name: englishReports.button })).toBeNull();
  });

  it("exports a run as Markdown and offers the download once the report is ready", async () => {
    let isReady = false;
    apiGet.mockImplementation((path) => {
      if (path !== FILE_PATH) {
        return Promise.reject(new Error(`No mocked response for ${path}`));
      }

      return Promise.resolve(
        isReady
          ? createSuccessResult({ url: DOWNLOAD_URL, expiresAt: "2026-11-01T11:00:00Z" })
          : createErrorResult(404, "NOT_FOUND"),
      );
    });
    const { container, queryClient } = renderButton({ source: "run", runId: RUN_ID });

    const dialog = await exportAs(format.md);

    expect(apiPost).toHaveBeenCalledWith("/api/projects/{project_key}/runs/{run_id}/export", {
      params: { path: { project_key: "SHOP", run_id: RUN_ID } },
      body: { format: "md" },
    });
    expect(
      await within(dialog).findByText(
        status.preparing.replace("{{fileName}}", "run-SHOP-1-2026-11-01.md"),
      ),
    ).toBeInTheDocument();
    await waitFor(() => {
      expect(apiGet).toHaveBeenCalledWith(FILE_PATH, {
        params: { path: { project_key: "SHOP", file_id: FILE_ID } },
        signal: expect.any(AbortSignal),
      });
    });
    expect(await axe(container)).toHaveNoViolations();

    isReady = true;
    await act(async () => {
      await queryClient.invalidateQueries({ queryKey: [GET_REPORT_LINK_KEY] });
    });

    const download = await within(dialog).findByRole("link", { name: status.download });
    expect(download).toHaveAttribute("href", DOWNLOAD_URL);
    expect(
      within(dialog).getByText(status.ready.replace("{{fileName}}", "run-SHOP-1-2026-11-01.md")),
    ).toBeInTheDocument();
  });

  it("exports a plan as PDF by default", async () => {
    const user = userEvent.setup();
    apiGet.mockResolvedValue(createErrorResult(404, "NOT_FOUND"));
    renderButton({ source: "plan", planId: PLAN_ID });

    await user.click(screen.getByRole("button", { name: englishReports.button }));
    const dialog = await screen.findByRole("dialog", { name: modal.title.plan });
    await user.click(within(dialog).getByRole("button", { name: modal.export }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith("/api/projects/{project_key}/plans/{plan_id}/export", {
        params: { path: { project_key: "SHOP", plan_id: PLAN_ID } },
        body: { format: "pdf" },
      });
    });
  });

  it("exports a story and says a notification follows when the file cannot be downloaded here", async () => {
    renderButton(
      { source: "story", jiraKey: "SHOP-1" },
      VIEWER_CAPABILITIES.filter((capability) => {
        return capability !== "file.download";
      }),
    );

    const dialog = await exportAs(format.md);

    expect(apiPost).toHaveBeenCalledWith("/api/projects/{project_key}/stories/{jira_key}/export", {
      params: { path: { project_key: "SHOP", jira_key: "SHOP-1" } },
      body: { format: "md" },
    });
    expect(
      await within(dialog).findByText(
        status.notifyLater.replace("{{fileName}}", "run-SHOP-1-2026-11-01.md"),
      ),
    ).toBeInTheDocument();
    expect(apiGet).not.toHaveBeenCalled();
  });
});
