import { TestProviders } from "@/test/test-providers";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSColorSchemeControl } from "./color-scheme-control";

const wrapper = ({ children }: { children: ReactNode }) => {
  return <TestProviders queryClient={createTestQueryClient()}>{children}</TestProviders>;
};

describe("DSColorSchemeControl", () => {
  it("reports the chosen color scheme", async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();
    render(<DSColorSchemeControl onChange={handleChange} />, { wrapper });

    await user.click(screen.getByRole("img", { name: "Dark" }));

    expect(handleChange).toHaveBeenCalledWith("dark");
  });

  it("works without a change handler", async () => {
    const user = userEvent.setup();
    render(<DSColorSchemeControl />, { wrapper });

    await user.click(screen.getByRole("img", { name: "Light" }));

    expect(screen.getByRole("radio", { name: "Light" })).toBeChecked();
  });

  it("moves between the options with the arrow keys and has no axe violations", async () => {
    const user = userEvent.setup();
    const { container } = render(<DSColorSchemeControl />, { wrapper });

    await user.click(screen.getByRole("img", { name: "Light" }));
    await user.keyboard("{ArrowRight}");

    expect(screen.getByRole("radio", { name: "Dark" })).toBeChecked();
    expect(await axe(container)).toHaveNoViolations();
  });
});
