import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSCheckbox } from "./checkbox";

describe("DSCheckbox", () => {
  it("calls onChange with true when an unchecked box is clicked", async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn<(isChecked: boolean) => void>();
    const { container } = render(
      <MantineProvider theme={mantineTheme} env="test">
        <DSCheckbox label="Remember me" isChecked={false} onChange={handleChange} />
      </MantineProvider>,
    );

    expect(await axe(container)).toHaveNoViolations();

    await user.click(screen.getByRole("checkbox", { name: "Remember me" }));

    expect(handleChange).toHaveBeenCalledWith(true);
  });
});
