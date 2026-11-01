import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSAlert } from "./alert";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSAlert", () => {
  it("exposes a danger alert with its title and no accessibility violations", async () => {
    const { container } = render(
      <DSAlert color="danger" title="Run aborted">
        The worker stopped responding.
      </DSAlert>,
      { wrapper },
    );

    const alert = screen.getByRole("alert");
    expect(alert).toHaveTextContent("Run aborted");
    expect(alert).toHaveTextContent("The worker stopped responding.");
    expect(await axe(container)).toHaveNoViolations();
  });

  it("uses the status role for informational alerts", () => {
    render(<DSAlert color="success">Saved</DSAlert>, { wrapper });

    expect(screen.getByRole("status")).toHaveTextContent("Saved");
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("renders the action and a labelled close button", async () => {
    const handleClose = vi.fn<() => void>();
    const { container } = render(
      <DSAlert
        color="warning"
        title="Jira is not configured"
        action={<a href="/settings">Configure</a>}
        closeLabel="Dismiss"
        onClose={handleClose}
      >
        Stories cannot sync.
      </DSAlert>,
      { wrapper },
    );

    expect(screen.getByRole("link", { name: "Configure" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Dismiss" }));
    expect(handleClose).toHaveBeenCalledTimes(1);
    expect(await axe(container)).toHaveNoViolations();
  });

  it("colours the title with the contrast-safe text token", () => {
    render(
      <DSAlert color="warning" title="Jira is not configured">
        Stories cannot sync.
      </DSAlert>,
      { wrapper },
    );

    expect(
      screen.getByText("Jira is not configured").closest(".mantine-Alert-title"),
    ).toHaveAttribute("style", expect.stringContaining("color: var(--color-yellow-text)"));
  });
});
