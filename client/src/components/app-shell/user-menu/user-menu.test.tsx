import { TestProviders } from "@/test/test-providers";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { UserMenu } from "./user-menu";

const { signOut, signOutState } = vi.hoisted(() => {
  return { signOut: vi.fn<() => void>(), signOutState: { isPending: false } };
});

vi.mock("next/navigation", () => {
  return {
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
      return { mutate: signOut, isPending: signOutState.isPending };
    },
  };
});

const renderUserMenu = (): ReturnType<typeof render> => {
  return render(
    <TestProviders queryClient={createTestQueryClient()}>
      <UserMenu />
    </TestProviders>,
  );
};

describe("UserMenu", () => {
  it("shows the user's name and email and signs out", async () => {
    signOutState.isPending = false;
    const { container } = renderUserMenu();
    const target = screen.getByRole("button", { name: "Account menu" });

    expect(target).toHaveTextContent("Lan Nguyen");
    expect(await axe(container)).toHaveNoViolations();

    await userEvent.click(target);

    expect(await screen.findByText("lan@example.com")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("menuitem", { name: "Sign out", hidden: true }));

    expect(signOut).toHaveBeenCalledTimes(1);
  });

  it("disables sign out while it is pending", async () => {
    signOutState.isPending = true;
    renderUserMenu();

    await userEvent.click(screen.getByRole("button", { name: "Account menu" }));

    expect(await screen.findByRole("menuitem", { name: "Sign out", hidden: true })).toBeDisabled();
  });
});
