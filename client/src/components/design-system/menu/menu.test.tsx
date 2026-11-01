import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSActionIcon } from "../action-icon/action-icon";
import { DSMenu } from "./menu";

vi.mock("next/navigation", () => {
  return {
    useRouter: () => {
      return { push: vi.fn(), replace: vi.fn(), prefetch: vi.fn() };
    },
  };
});

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSMenu", () => {
  it("opens on target click and calls the item onClick", async () => {
    const handleArchive = vi.fn<() => void>();
    render(
      <DSMenu
        target={<DSActionIcon icon="dots" ariaLabel="Project actions" />}
        items={[
          { key: "heading", type: "label", label: "Project" },
          { key: "settings", label: "Settings", icon: "settings", href: "/settings" },
          { key: "divider", type: "divider" },
          {
            key: "archive",
            label: "Archive",
            icon: "trash",
            isDanger: true,
            onClick: handleArchive,
          },
        ]}
      />,
      { wrapper },
    );

    const target = screen.getByRole("button", { name: "Project actions" });
    expect(screen.queryByRole("menu")).not.toBeInTheDocument();

    await userEvent.click(target);

    expect(screen.getByRole("menu")).toBeInTheDocument();
    expect(target).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByText("Project")).toBeInTheDocument();
    expect(document.querySelector(".mantine-Menu-divider")).toBeInTheDocument();
    expect(screen.getByRole("menuitem", { name: "Settings" })).toHaveAttribute("href", "/settings");

    await userEvent.click(screen.getByRole("menuitem", { name: "Archive" }));

    expect(handleArchive).toHaveBeenCalledTimes(1);
  });

  it("opens from the keyboard, moves with the arrow keys, closes on Escape and returns focus", async () => {
    const user = userEvent.setup();
    render(
      <DSMenu
        target={<DSActionIcon icon="dots" ariaLabel="Project actions" />}
        items={[
          { key: "settings", label: "Settings", icon: "settings", href: "/settings" },
          { key: "archive", label: "Archive", icon: "trash", isDanger: true, onClick: vi.fn() },
        ]}
      />,
      { wrapper },
    );

    const target = screen.getByRole("button", { name: "Project actions" });
    await user.tab();
    expect(target).toHaveFocus();
    await user.keyboard("{Enter}");

    expect(await screen.findByRole("menu")).toBeInTheDocument();
    expect(await axe(screen.getByRole("menu"))).toHaveNoViolations();

    await waitFor(() => {
      expect(screen.getByRole("menuitem", { name: "Settings" })).toHaveFocus();
    });
    await user.keyboard("{ArrowDown}");
    expect(screen.getByRole("menuitem", { name: "Archive" })).toHaveFocus();
    await user.keyboard("{ArrowUp}");
    expect(screen.getByRole("menuitem", { name: "Settings" })).toHaveFocus();

    await user.keyboard("{Escape}");
    await waitFor(() => {
      expect(screen.queryByRole("menu")).not.toBeInTheDocument();
    });
    expect(target).toHaveFocus();
  });
});
