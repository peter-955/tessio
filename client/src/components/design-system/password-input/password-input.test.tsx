import { createI18nInstance } from "@/lib/i18n";
import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { Language } from "@/shared/typing/enums/language.enum";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { I18nextProvider } from "react-i18next";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSPasswordInput } from "./password-input";

const findVisibilityToggle = (container: HTMLElement): Element | null => {
  return container.querySelector(".mantine-PasswordInput-visibilityToggle");
};

describe("DSPasswordInput", () => {
  it("labels the visibility toggle from the common namespace when no label is given", () => {
    const handleChange = vi.fn<(value: string) => void>();
    const { container } = render(
      <I18nextProvider i18n={createI18nInstance(Language.FRENCH)}>
        <MantineProvider theme={mantineTheme} env="test">
          <DSPasswordInput
            label="Mot de passe"
            value=""
            onChange={handleChange}
            autoComplete="current-password"
          />
        </MantineProvider>
      </I18nextProvider>,
    );

    expect(findVisibilityToggle(container)).toHaveAttribute(
      "aria-label",
      "Afficher ou masquer le mot de passe",
    );
  });

  it("uses the caller's visibility toggle label when it is given", () => {
    const handleChange = vi.fn<(value: string) => void>();
    const { container } = render(
      <I18nextProvider i18n={createI18nInstance(Language.ENGLISH)}>
        <MantineProvider theme={mantineTheme} env="test">
          <DSPasswordInput
            label="Password"
            value=""
            onChange={handleChange}
            autoComplete="new-password"
            visibilityToggleLabel="Reveal password"
          />
        </MantineProvider>
      </I18nextProvider>,
    );

    expect(findVisibilityToggle(container)).toHaveAttribute("aria-label", "Reveal password");
  });

  it("toggles the visibility from the keyboard and has no axe violations", async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn<(value: string) => void>();
    const { container } = render(
      <I18nextProvider i18n={createI18nInstance(Language.ENGLISH)}>
        <MantineProvider theme={mantineTheme} env="test">
          <DSPasswordInput
            label="Password"
            value="secret"
            onChange={handleChange}
            autoComplete="current-password"
          />
        </MantineProvider>
      </I18nextProvider>,
    );

    const input = screen.getByLabelText("Password");
    expect(input).toHaveAttribute("type", "password");
    await user.tab();
    expect(input).toHaveFocus();
    await user.tab();
    expect(screen.getByRole("button", { name: "Show or hide password" })).toHaveFocus();
    await user.keyboard("{Enter}");
    expect(input).toHaveAttribute("type", "text");
    expect(await axe(container)).toHaveNoViolations();
  });
});
