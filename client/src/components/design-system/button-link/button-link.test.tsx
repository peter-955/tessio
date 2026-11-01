import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { DSButtonLink } from "./button-link";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSButtonLink", () => {
  it("renders an internal link", () => {
    render(<DSButtonLink href="/projects/SHOP/runs">Open runs</DSButtonLink>, { wrapper });

    const link = screen.getByRole("link", { name: "Open runs" });
    expect(link).toHaveAttribute("href", "/projects/SHOP/runs");
    expect(link).not.toHaveAttribute("target");
  });

  it("opens external links in a new tab safely", () => {
    render(
      <DSButtonLink href="https://jira.example.test" isExternal hasArrow>
        Open Jira
      </DSButtonLink>,
      { wrapper },
    );

    const link = screen.getByRole("link", { name: "Open Jira" });
    expect(link).toHaveAttribute("href", "https://jira.example.test");
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");
  });

  it("is reached with Tab and has no axe violations", async () => {
    const user = userEvent.setup();
    const { container } = render(
      <DSButtonLink href="/projects/SHOP/runs" type="primary">
        Open runs
      </DSButtonLink>,
      { wrapper },
    );

    await user.tab();
    expect(screen.getByRole("link", { name: "Open runs" })).toHaveFocus();
    expect(await axe(container)).toHaveNoViolations();
  });
});
