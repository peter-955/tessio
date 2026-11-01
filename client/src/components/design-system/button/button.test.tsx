import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSButton } from "./button";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSButton", () => {
  it("renders the aria attributes when they are passed", () => {
    render(
      <>
        <DSButton
          ariaExpanded={false}
          ariaControls="steps-panel"
          ariaHasPopup="menu"
          ariaLabel="Show the steps of TC-1"
        >
          Show steps
        </DSButton>
        <div id="steps-panel" hidden />
      </>,
      { wrapper },
    );

    const button = screen.getByRole("button", { name: "Show the steps of TC-1" });
    expect(button).toHaveAttribute("aria-expanded", "false");
    expect(button).toHaveAttribute("aria-controls", "steps-panel");
    expect(button).toHaveAttribute("aria-haspopup", "menu");
  });

  it("renders no aria attributes when none are passed", () => {
    render(<DSButton>Save</DSButton>, { wrapper });

    const button = screen.getByRole("button", { name: "Save" });
    expect(button).not.toHaveAttribute("aria-expanded");
    expect(button).not.toHaveAttribute("aria-controls");
    expect(button).not.toHaveAttribute("aria-haspopup");
    expect(button).not.toHaveAttribute("aria-label");
  });

  it("is reached with Tab, runs onClick on Enter and has no axe violations", async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn<() => void>();
    const { container } = render(
      <>
        <DSButton type="primary" ariaExpanded={true} ariaControls="panel" onClick={handleClick}>
          Hide steps
        </DSButton>
        <div id="panel">Steps</div>
      </>,
      { wrapper },
    );

    await user.tab();
    expect(screen.getByRole("button", { name: "Hide steps" })).toHaveFocus();
    await user.keyboard("{Enter}");
    expect(handleClick).toHaveBeenCalledTimes(1);
    expect(await axe(container)).toHaveNoViolations();
  });
});
