import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { DSTooltip } from "./tooltip";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSTooltip", () => {
  it("shows the label when the target is focused", async () => {
    render(
      <DSTooltip label="Copied to clipboard">
        <button type="button">Copy</button>
      </DSTooltip>,
      { wrapper },
    );

    await userEvent.tab();
    expect(await screen.findByRole("tooltip")).toHaveTextContent("Copied to clipboard");
  });

  it("stays hidden when disabled", async () => {
    render(
      <DSTooltip label="Copied to clipboard" isDisabled>
        <button type="button">Copy</button>
      </DSTooltip>,
      { wrapper },
    );

    await userEvent.tab();
    expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
  });

  it("describes the focused target, hides on Escape and has no axe violations", async () => {
    const user = userEvent.setup();
    const { container } = render(
      <DSTooltip label="Copied to clipboard">
        <button type="button">Copy</button>
      </DSTooltip>,
      { wrapper },
    );

    await user.tab();
    expect(await screen.findByRole("tooltip")).toHaveTextContent("Copied to clipboard");
    expect(await axe(container)).toHaveNoViolations();
    expect(await axe(screen.getByRole("tooltip"))).toHaveNoViolations();
    await user.keyboard("{Escape}");
    await waitFor(() => {
      expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
    });
    expect(screen.getByRole("button", { name: "Copy" })).toHaveFocus();
  });
});
