import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSActionIcon } from "./action-icon";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSActionIcon", () => {
  it("has an accessible name and calls onClick", async () => {
    const handleClick = vi.fn<() => void>();
    render(<DSActionIcon icon="trash" ariaLabel="Delete file" onClick={handleClick} />, {
      wrapper,
    });

    await userEvent.click(screen.getByRole("button", { name: "Delete file" }));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("is disabled when isDisabled", () => {
    render(<DSActionIcon icon="trash" ariaLabel="Delete file" isDisabled />, { wrapper });

    expect(screen.getByRole("button", { name: "Delete file" })).toBeDisabled();
  });

  it("shows the label as a tooltip on hover", async () => {
    render(<DSActionIcon icon="copy" ariaLabel="Copy key" hasTooltip />, { wrapper });

    await userEvent.hover(screen.getByRole("button", { name: "Copy key" }));
    expect(await screen.findByRole("tooltip")).toHaveTextContent("Copy key");
  });

  it("has no axe violations", async () => {
    const { container } = render(
      <>
        <DSActionIcon icon="trash" ariaLabel="Delete file" />
        <DSActionIcon icon="copy" ariaLabel="Copy key" hasTooltip />
      </>,
      { wrapper },
    );

    expect(await axe(container)).toHaveNoViolations();
  });
});
