import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSSelect } from "./select";
import type { DSSelectOption } from "./select.type";

type Role = "viewer" | "editor";

const ROLE_OPTIONS: DSSelectOption<Role>[] = [
  { value: "viewer", label: "Viewer" },
  { value: "editor", label: "Editor" },
];

describe("DSSelect", () => {
  it("calls onChange with the typed value of the chosen option", async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn<(value: Role | null) => void>();
    const { container } = render(
      <MantineProvider theme={mantineTheme} env="test">
        <DSSelect<Role> label="Role" value={null} options={ROLE_OPTIONS} onChange={handleChange} />
      </MantineProvider>,
    );

    expect(await axe(container)).toHaveNoViolations();

    await user.click(screen.getByRole("combobox", { name: "Role" }));
    await user.click(await screen.findByRole("option", { name: "Editor" }));

    expect(handleChange).toHaveBeenCalledWith("editor");
  });
});
