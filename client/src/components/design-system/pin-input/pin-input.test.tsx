import { createI18nInstance } from "@/lib/i18n";
import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { Language } from "@/shared/typing/enums/language.enum";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState, type FC } from "react";
import { I18nextProvider } from "react-i18next";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSPinInput } from "./pin-input";

interface Props {
  language: Language;
  ariaLabel: string;
  onComplete: (value: string) => void;
}

const ControlledPinInput: FC<Props> = ({ language, ariaLabel, onComplete }) => {
  const [code, setCode] = useState("");
  const [i18n] = useState(() => {
    return createI18nInstance(language);
  });

  return (
    <I18nextProvider i18n={i18n}>
      <MantineProvider theme={mantineTheme} env="test">
        <DSPinInput
          value={code}
          onChange={setCode}
          onComplete={onComplete}
          ariaLabel={ariaLabel}
          isAutoFocused={false}
        />
      </MantineProvider>
    </I18nextProvider>
  );
};

describe("DSPinInput", () => {
  it("renders 6 numeric one-time-code inputs and calls onComplete with the 6 digits", async () => {
    const user = userEvent.setup();
    const handleComplete = vi.fn<(value: string) => void>();
    const { container } = render(
      <ControlledPinInput
        language={Language.ENGLISH}
        ariaLabel="Authentication code"
        onComplete={handleComplete}
      />,
    );

    expect(await axe(container)).toHaveNoViolations();

    const inputs = screen.getAllByRole("textbox");

    expect(inputs).toHaveLength(6);
    expect(inputs[0]).toHaveAttribute("inputmode", "numeric");
    expect(inputs[0]).toHaveAttribute("autocomplete", "one-time-code");

    await user.click(inputs[0]);
    await user.keyboard("123456");

    expect(handleComplete).toHaveBeenCalledWith("123456");
  });

  it("gives the group and every digit a translated accessible name", () => {
    const handleComplete = vi.fn<(value: string) => void>();
    render(
      <ControlledPinInput
        language={Language.FRENCH}
        ariaLabel="Code d'authentification"
        onComplete={handleComplete}
      />,
    );

    expect(screen.getByRole("group", { name: "Code d'authentification" })).toBeInTheDocument();

    const accessibleNames = screen.getAllByRole("textbox").map((input) => {
      return input.getAttribute("aria-label");
    });

    expect(accessibleNames).toEqual([
      "Code d'authentification, chiffre 1 sur 6",
      "Code d'authentification, chiffre 2 sur 6",
      "Code d'authentification, chiffre 3 sur 6",
      "Code d'authentification, chiffre 4 sur 6",
      "Code d'authentification, chiffre 5 sur 6",
      "Code d'authentification, chiffre 6 sur 6",
    ]);
  });
});
