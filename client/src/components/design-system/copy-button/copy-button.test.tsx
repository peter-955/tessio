import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSCopyButton } from "./copy-button";

vi.mock("react-i18next", () => {
  return {
    useTranslation: () => {
      return { t: (key: string): string => key };
    },
  };
});

describe("DSCopyButton", () => {
  it("writes the value to the clipboard and shows the copied state", async () => {
    const user = userEvent.setup();
    const writeText = vi.spyOn(navigator.clipboard, "writeText");
    const { container } = render(
      <MantineProvider theme={mantineTheme} env="test">
        <DSCopyButton value="tessio_token_value" />
      </MantineProvider>,
    );

    expect(await axe(container)).toHaveNoViolations();

    await user.click(screen.getByRole("button", { name: "actions.copy" }));

    expect(writeText).toHaveBeenCalledWith("tessio_token_value");
    expect(await screen.findByRole("button", { name: "actions.copied" })).toBeInTheDocument();
  });

  it("copies with the keyboard when it is focused and Enter is pressed", async () => {
    const user = userEvent.setup();
    const writeText = vi.spyOn(navigator.clipboard, "writeText");
    render(
      <MantineProvider theme={mantineTheme} env="test">
        <DSCopyButton value="npx tessio install" label="Copy command" />
      </MantineProvider>,
    );

    expect(screen.getByRole("button", { name: "Copy command" })).toBeInTheDocument();

    await user.tab();
    await user.keyboard("{Enter}");

    expect(writeText).toHaveBeenCalledWith("npx tessio install");
    expect(screen.getByRole("button", { name: "Copy command" })).toBeInTheDocument();
    expect(await screen.findByRole("status")).toHaveTextContent("actions.copied");
    expect(await screen.findByRole("tooltip")).toHaveTextContent("actions.copied");
  });

  it("returns to the copy state after the timeout", async () => {
    const user = userEvent.setup();
    render(
      <MantineProvider theme={mantineTheme} env="test">
        <DSCopyButton value="tessio_token_value" timeoutInMilliseconds={50} />
      </MantineProvider>,
    );

    await user.click(screen.getByRole("button", { name: "actions.copy" }));

    expect(await screen.findByRole("button", { name: "actions.copied" })).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "actions.copy" })).toBeInTheDocument();
    });
  });
});
