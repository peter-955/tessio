import type { ApiResponseStub } from "@/components/project-context/test/utils/api-response.util";
import {
  buildErrorResponse,
  buildSuccessResponse,
} from "@/components/project-context/test/utils/api-response.util";
import { buildProject } from "@/components/project-context/test/utils/project-fixture.util";
import { renderHookWithProviders } from "@/test/utils/render-hook-with-providers.util";
import { waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GET_PROJECT_KEY, useGetProject } from "./use-get-project";
import { GET_PROJECT_MEMBERS_KEY, useGetProjectMembers } from "./use-get-project-members";
import { GET_PROJECTS_KEY, useGetProjects } from "./use-get-projects";

const { getRequest } = vi.hoisted(() => {
  return { getRequest: vi.fn<(path: string, options?: unknown) => Promise<ApiResponseStub>>() };
});

vi.mock("@/lib/api/api-client", () => {
  return { apiClient: { GET: getRequest, POST: vi.fn() } };
});

describe("useGetProject", () => {
  it("requests the project by its key", async () => {
    const project = buildProject();
    getRequest.mockResolvedValue(buildSuccessResponse(project));

    const { result, queryClient } = renderHookWithProviders(() => {
      return useGetProject("SHOP");
    });

    await waitFor(() => {
      expect(result.current.data).toEqual(project);
    });
    expect(getRequest).toHaveBeenCalledWith("/api/projects/{project_key}", {
      params: { path: { project_key: "SHOP" } },
    });
    expect(queryClient.getQueryData([GET_PROJECT_KEY, "SHOP"])).toEqual(project);
  });

  it("exposes the API error status", async () => {
    getRequest.mockResolvedValue(buildErrorResponse(404, "NOT_FOUND"));

    const { result } = renderHookWithProviders(() => {
      return useGetProject("GONE");
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });
    expect(result.current.error?.status).toBe(404);
  });

  it("does not request without a project key", () => {
    const { result } = renderHookWithProviders(() => {
      return useGetProject(null);
    });

    expect(result.current.isPending).toBe(true);
    expect(result.current.isFetching).toBe(false);
    expect(getRequest).not.toHaveBeenCalled();
  });
});

describe("useGetProjects", () => {
  it("lists the projects without the archived ones by default", async () => {
    const projects = [buildProject()];
    getRequest.mockResolvedValue(buildSuccessResponse(projects));

    const { result, queryClient } = renderHookWithProviders(() => {
      return useGetProjects();
    });

    await waitFor(() => {
      expect(result.current.data).toEqual(projects);
    });
    expect(getRequest).toHaveBeenCalledWith("/api/projects", {
      params: { query: { includeArchived: false } },
    });
    expect(queryClient.getQueryData([GET_PROJECTS_KEY, false])).toEqual(projects);
  });

  it("includes the archived projects on request", async () => {
    getRequest.mockResolvedValue(buildSuccessResponse([]));

    renderHookWithProviders(() => {
      return useGetProjects({ isIncludingArchived: true });
    });

    await waitFor(() => {
      expect(getRequest).toHaveBeenCalledWith("/api/projects", {
        params: { query: { includeArchived: true } },
      });
    });
  });
});

describe("useGetProjectMembers", () => {
  it("lists the members of the project", async () => {
    getRequest.mockResolvedValue(buildSuccessResponse([]));

    const { result, queryClient } = renderHookWithProviders(() => {
      return useGetProjectMembers("SHOP");
    });

    await waitFor(() => {
      expect(result.current.data).toEqual([]);
    });
    expect(getRequest).toHaveBeenCalledWith("/api/projects/{project_key}/members", {
      params: { path: { project_key: "SHOP" } },
    });
    expect(queryClient.getQueryData([GET_PROJECT_MEMBERS_KEY, "SHOP"])).toEqual([]);
  });
});
