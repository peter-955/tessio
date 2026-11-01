"use client";

import {
  DSCard,
  DSSegmentedControl,
  DSSelect,
  DSStack,
  DSText,
  useDSColorScheme,
  type DSSegmentedOption,
} from "@/components/design-system";
import { useLanguage } from "@/shared/hooks/use-language";
import type { Language } from "@/shared/typing/enums/language.enum";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useSaveColorScheme } from "../../hooks/use-save-color-scheme";
import { useSaveLanguage } from "../../hooks/use-save-language";
import { LANGUAGE_NAME_OPTIONS } from "../../typing/constants/profile.constant";
import type { ColorScheme } from "../../typing/types/color-scheme.type";
import styles from "./preferences-card.module.scss";

export const PreferencesCard: FC = () => {
  const { t } = useTranslation("profile");
  const { t: translateCommon } = useTranslation();
  const { colorScheme, setColorScheme } = useDSColorScheme();
  const { language } = useLanguage();
  const saveColorScheme = useSaveColorScheme();
  const saveLanguage = useSaveLanguage();

  const colorSchemeOptions: DSSegmentedOption<ColorScheme>[] = [
    { value: "light", label: translateCommon("colorScheme.light") },
    { value: "dark", label: translateCommon("colorScheme.dark") },
    { value: "auto", label: translateCommon("colorScheme.auto") },
  ];

  const handleColorSchemeChange = (value: ColorScheme): void => {
    setColorScheme(value);
    saveColorScheme(value);
  };

  const handleLanguageChange = (value: Language | null): void => {
    if (value !== null) {
      saveLanguage(value);
    }
  };

  return (
    <DSCard title={t("preferences.title")}>
      <DSStack gap={4}>
        <DSText size="sm" color="muted">
          {t("preferences.description")}
        </DSText>
        <div className={styles.fields}>
          <DSStack gap={1}>
            <DSText size="sm" weight="medium" component="span">
              {t("preferences.theme")}
            </DSText>
            <DSSegmentedControl
              value={colorScheme}
              options={colorSchemeOptions}
              onChange={handleColorSchemeChange}
              ariaLabel={t("preferences.theme")}
              isFullWidth
            />
          </DSStack>
          <DSSelect
            label={t("preferences.language")}
            value={language}
            options={LANGUAGE_NAME_OPTIONS}
            onChange={handleLanguageChange}
          />
        </div>
      </DSStack>
    </DSCard>
  );
};
