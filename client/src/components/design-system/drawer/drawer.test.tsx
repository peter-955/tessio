import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSDrawer } from "./drawer";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSDrawer", () => {
  it("renders the title, content and footer when opened and closes from the close button", async () => {
    const handleClose = vi.fn<() => void>();
    render(
      <DSDrawer
        isOpened
        onClose={handleClose}
        title="Run details"
        closeLabel="Close drawer"
        footer={<button type="button">Save</button>}
      >
        Drawer content
      </DSDrawer>,
      { wrapper },
    );

    expect(screen.getByRole("dialog", { name: "Run details" })).toBeInTheDocument();
    expect(screen.getByText("Drawer content")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Save" })).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Close drawer" }));
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it("renders nothing when closed", () => {
    render(
      <DSDrawer isOpened={false} onClose={vi.fn()} title="Run details" closeLabel="Close drawer">
        Drawer content
      </DSDrawer>,
      { wrapper },
    );

    expect(screen.queryByText("Run details")).not.toBeInTheDocument();
  });

  it("closes on Escape and has no axe violations", async () => {
    const user = userEvent.setup();
    const handleClose = vi.fn<() => void>();
    render(
      <DSDrawer isOpened onClose={handleClose} title="Run details" closeLabel="Close drawer">
        <button type="button">Save</button>
      </DSDrawer>,
      { wrapper },
    );

    const dialog = await screen.findByRole("dialog", { name: "Run details" });
    expect(await axe(dialog)).toHaveNoViolations();
    await user.keyboard("{Escape}");
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
