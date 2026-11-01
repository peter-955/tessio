import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSErrorState } from "./error-state";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSErrorState", () => {
  it("calls onRetry from the retry button", async () => {
    const handleRetry = vi.fn<() => void>();
    const { container } = render(
      <DSErrorState
        title="Could not load runs"
        description="Check your connection."
        retryLabel="Try again"
        onRetry={handleRetry}
      />,
      { wrapper },
    );

    expect(screen.getByRole("alert")).toHaveTextContent("Could not load runs");
    await userEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(handleRetry).toHaveBeenCalledTimes(1);
    expect(await axe(container)).toHaveNoViolations();
  });

  it("hides the retry button without onRetry", () => {
    render(<DSErrorState title="Could not load runs" />, { wrapper });

    expect(screen.getByRole("alert")).toHaveTextContent("Could not load runs");
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});
