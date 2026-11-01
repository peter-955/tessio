"use client";

import { useDSColorScheme } from "@/components/design-system";
import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";
import { useLanguage } from "@/shared/hooks/use-language";
import { isLanguage } from "@/shared/utils/language.util";
import { useEffect, useRef, type FC } from "react";
import type { ColorScheme } from "../../typing/types/color-scheme.type";

export const SavedPreferencesSync: FC = () => {
  const { colorScheme: savedColorScheme, language: savedLanguage } = useCurrentUser();
  const { colorScheme, setColorScheme } = useDSColorScheme();
  const { language, changeLanguage } = useLanguage();
  const appliedColorSchemeRef = useRef<ColorScheme | null>(null);
  const appliedLanguageRef = useRef<string | null>(null);

  useEffect(() => {
    if (appliedColorSchemeRef.current === savedColorScheme) {
      return;
    }
    appliedColorSchemeRef.current = savedColorScheme;
    if (colorScheme !== savedColorScheme) {
      setColorScheme(savedColorScheme);
    }
  }, [colorScheme, savedColorScheme, setColorScheme]);

  useEffect(() => {
    if (appliedLanguageRef.current === savedLanguage) {
      return;
    }
    appliedLanguageRef.current = savedLanguage;
    if (isLanguage(savedLanguage) && language !== savedLanguage) {
      changeLanguage(savedLanguage);
    }
  }, [changeLanguage, language, savedLanguage]);

  return null;
};
