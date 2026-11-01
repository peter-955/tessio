"use client";

import type { MantineColorScheme } from "@mantine/core";
import { SegmentedControl, useMantineColorScheme } from "@mantine/core";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { DSIcon } from "../icon/icon";
import { isColorScheme } from "../utils/color-scheme.util";
import styles from "./color-scheme-control.module.scss";

interface Props {
  onChange?: (colorScheme: MantineColorScheme) => void;
}

export const DSColorSchemeControl: FC<Props> = ({ onChange }) => {
  const { t } = useTranslation();
  const { colorScheme, setColorScheme } = useMantineColorScheme();

  const options = [
    { value: "light", label: <DSIcon name="sun" size={16} />, title: t("colorScheme.light") },
    { value: "dark", label: <DSIcon name="moon" size={16} />, title: t("colorScheme.dark") },
    { value: "auto", label: <DSIcon name="system" size={16} />, title: t("colorScheme.auto") },
  ].map((option) => {
    return {
      value: option.value,
      label: (
        <span className={styles.option} title={option.title} role="img" aria-label={option.title}>
          {option.label}
        </span>
      ),
    };
  });

  const handleChange = (value: string): void => {
    if (isColorScheme(value)) {
      setColorScheme(value);
      onChange?.(value);
    }
  };

  return (
    <SegmentedControl
      value={colorScheme}
      data={options}
      onChange={handleChange}
      size="xs"
      fullWidth
      aria-label={t("colorScheme.label")}
    />
  );
};
