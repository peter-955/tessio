"use client";

import { useDSColorScheme } from "@/components/design-system";
import { useLanguage } from "@/shared/hooks/use-language";
import type { FC } from "react";

export const PreferencesProbe: FC = () => {
  const { colorScheme, setColorScheme } = useDSColorScheme();
  const { language } = useLanguage();

  const handleUseLight = (): void => {
    setColorScheme("light");
  };

  return (
    <div>
      <p data-testid="color-scheme">{colorScheme}</p>
      <p data-testid="language">{language}</p>
      <button type="button" onClick={handleUseLight}>
        Use light
      </button>
    </div>
  );
};
