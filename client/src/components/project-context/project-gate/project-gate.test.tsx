import { TestProviders } from "@/test/test-providers";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { FC } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { useCurrentProject } from "../hooks/use-current-project";
import {
  buildErrorResponse,
  buildSuccessResponse,
  type ApiResponseStub,
} from "../test/utils/api-response.util";
import { buildProject } from "../test/utils/project-fixture.util";
import { readLastProjectKey, storeLastProjectKey } from "../utils/last-project-key.util";
import { ProjectGate } from "./project-gate";

const { getRequest } = vi.hoisted(() => {
  return { getRequest: vi.fn<(path: string, options?: unknown) => Promise<ApiResponseStub>>() };
});

vi.mock("@/lib/api/api-client", () => {
  return { apiClient: { GET: getRequest, POST: vi.fn() } };
});

vi.mock("next/navigation", () => {
  return {
    useRouter: () => {
      return { push: vi.fn(), replace: vi.fn(), prefetch: vi.fn() };
    },
  };
});

const CurrentProjectName: FC = () => {
  const project = useCurrentProject();

  return <h1>{project.name}</h1>;
};

const renderGate = (projectKey = "SHOP"): ReturnType<typeof render> => {
  return render(
    <TestProviders queryClient={createTestQueryClient()}>
      <ProjectGate projectKey={projectKey}>
        <CurrentProjectName />
      </ProjectGate>
    </TestProviders>,
  );
};

const waitForever = (): Promise<ApiResponseStub> => {
  return new Promise(() => {
    return;
  });
};

afterEach(() => {
  window.localStorage.clear();
});

describe("ProjectGate", () => {
  it("shows a skeleton while the project loads", async () => {
    getRequest.mockImplementation(waitForever);

    const { container } = renderGate();

    expect(screen.getByLabelText("Loading the project")).toHaveAttribute("aria-busy", "true");
    expect(screen.queryByRole("heading")).not.toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("renders the children with the current project and remembers it", async () => {
    getRequest.mockResolvedValue(buildSuccessResponse(buildProject()));

    const { container } = renderGate();

    expect(await screen.findByRole("heading", { name: "Shop" })).toBeInTheDocument();
    expect(screen.queryByText("This project is archived")).not.toBeInTheDocument();
    expect(readLastProjectKey()).toBe("SHOP");
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the archived banner and does not remember an archived project", async () => {
    getRequest.mockResolvedValue(
      buildSuccessResponse(buildProject({ isArchived: true, archivedAt: "2026-10-20T09:00:00Z" })),
    );

    const { container } = renderGate();

    expect(await screen.findByRole("heading", { name: "Shop" })).toBeInTheDocument();
    expect(screen.getByText("This project is archived")).toBeInTheDocument();
    expect(
      screen.getByText("You can still view everything, but nothing can be changed."),
    ).toBeInTheDocument();
    expect(readLastProjectKey()).toBeNull();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the not-found view and forgets the project on a 404", async () => {
    storeLastProjectKey("GONE");
    getRequest.mockResolvedValue(buildErrorResponse(404, "NOT_FOUND"));

    const { container } = renderGate("GONE");

    expect(await screen.findByText("Project not found")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "See your projects" })).toHaveAttribute(
      "href",
      "/projects",
    );
    expect(readLastProjectKey()).toBeNull();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows a retryable error state on other errors", async () => {
    getRequest.mockResolvedValue(buildErrorResponse(500, "INTERNAL_ERROR"));

    const { container } = renderGate();

    expect(await screen.findByRole("alert")).toHaveTextContent("This project could not be loaded");
    expect(getRequest).toHaveBeenCalledTimes(1);
    expect(await axe(container)).toHaveNoViolations();

    getRequest.mockResolvedValue(buildSuccessResponse(buildProject()));
    await userEvent.click(screen.getByRole("button", { name: "Try again" }));

    expect(await screen.findByRole("heading", { name: "Shop" })).toBeInTheDocument();
    expect(getRequest).toHaveBeenCalledTimes(2);
  });
});

describe("useCurrentProject", () => {
  it("throws outside ProjectGate", () => {
    vi.spyOn(console, "error").mockImplementation(() => {
      return;
    });

    expect(() => {
      return render(
        <TestProviders queryClient={createTestQueryClient()}>
          <CurrentProjectName />
        </TestProviders>,
      );
    }).toThrow("useCurrentProject must be used inside ProjectGate");
  });
});
