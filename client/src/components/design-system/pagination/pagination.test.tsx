import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSPagination } from "./pagination";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSPagination", () => {
  it("calls onChange with the next page without accessibility violations", async () => {
    const handleChange = vi.fn<(page: number) => void>();
    const { container } = render(
      <DSPagination
        page={2}
        pageCount={5}
        onChange={handleChange}
        ariaLabel="Runs pages"
        previousLabel="Previous page"
        nextLabel="Next page"
      />,
      { wrapper },
    );

    expect(screen.getByRole("navigation", { name: "Runs pages" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Next page" }));
    expect(handleChange).toHaveBeenCalledWith(3);
    await userEvent.click(screen.getByRole("button", { name: "Previous page" }));
    expect(handleChange).toHaveBeenCalledWith(1);
    expect(await axe(container)).toHaveNoViolations();
  });

  it("is hidden with a single page", () => {
    render(
      <DSPagination
        page={1}
        pageCount={1}
        onChange={vi.fn()}
        ariaLabel="Runs pages"
        previousLabel="Previous page"
        nextLabel="Next page"
      />,
      { wrapper },
    );

    expect(screen.queryByRole("navigation")).not.toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});
