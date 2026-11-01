import type { ApiResponseStub } from "@/components/project-context/test/utils/api-response.util";
import { TestProviders } from "@/test/test-providers";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { AppShell } from "./app-shell";

const { getRequest } = vi.hoisted(() => {
  return { getRequest: vi.fn<(path: string, options?: unknown) => Promise<ApiResponseStub>>() };
});

vi.mock("@/lib/api/api-client", () => {
  return { apiClient: { GET: getRequest, POST: vi.fn() } };
});

vi.mock("next/navigation", () => {
  return {
    usePathname: () => {
      return "/projects";
    },
    useParams: () => {
      return {};
    },
    useRouter: () => {
      return { push: vi.fn(), replace: vi.fn(), prefetch: vi.fn() };
    },
  };
});

vi.mock("@/components/session-guard/hooks/use-current-user", () => {
  return {
    useCurrentUser: () => {
      return {
        id: "0b7f4a8e-3c55-4f5e-8f3e-2a0c9f1d6b21",
        email: "lan@example.com",
        name: "Lan Nguyen",
        workspaceRole: "member",
        nextStep: "signed_in",
      };
    },
  };
});

vi.mock("@/modules/auth/hooks/mutations/use-post-sign-out", () => {
  return {
    usePostSignOut: () => {
      return { mutate: vi.fn(), isPending: false };
    },
  };
});

describe("AppShell", () => {
  it("renders the sidebar, the top bar and the page", () => {
    getRequest.mockResolvedValue({ data: [], response: new Response(null, { status: 200 }) });

    render(
      <TestProviders queryClient={createTestQueryClient()}>
        <AppShell>
          <h1>Projects page</h1>
        </AppShell>
      </TestProviders>,
    );

    expect(screen.getByRole("main")).toHaveTextContent("Projects page");
    expect(screen.getByRole("complementary")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Choose a project" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Search" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Account menu" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Notifications" })).toBeInTheDocument();
  });

  it("opens the navigation drawer and closes it when a link is chosen", async () => {
    getRequest.mockResolvedValue({ data: [], response: new Response(null, { status: 200 }) });

    render(
      <TestProviders queryClient={createTestQueryClient()}>
        <AppShell>
          <h1>Projects page</h1>
        </AppShell>
      </TestProviders>,
    );

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Open navigation" }));

    const drawer = await screen.findByRole("dialog", { name: "Navigation" });
    expect(
      within(drawer).getByRole("navigation", { name: "Workspace navigation" }),
    ).toBeInTheDocument();

    await userEvent.click(within(drawer).getByRole("link", { name: "Projects" }));

    await waitFor(() => {
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });
  });

  it("starts with a skip link to the main content and has no axe violations", async () => {
    const user = userEvent.setup();
    getRequest.mockResolvedValue({ data: [], response: new Response(null, { status: 200 }) });

    const { container } = render(
      <TestProviders queryClient={createTestQueryClient()}>
        <AppShell>
          <h1>Projects page</h1>
        </AppShell>
      </TestProviders>,
    );

    await user.tab();
    const skipLink = screen.getByRole("link", { name: "Skip to main content" });
    expect(skipLink).toHaveFocus();
    expect(skipLink).toHaveAttribute("href", "#main-content");
    const main = screen.getByRole("main");
    expect(main).toHaveAttribute("id", "main-content");
    expect(main).toHaveAttribute("tabindex", "-1");
    expect(await axe(container)).toHaveNoViolations();
  });
});
