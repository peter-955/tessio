"use client";

import { DSButton } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import styles from "./search-placeholder.module.scss";

export const SearchPlaceholder: FC = () => {
  const { t } = useTranslation();

  return (
    <span className={styles.search}>
      <DSButton
        type="default"
        icon="search"
        isDisabled
        isFullWidth
        title={t("appShell.search.comingSoon")}
      >
        {t("appShell.search.label")}
      </DSButton>
      <span className={styles.visuallyHidden}>{t("appShell.search.comingSoon")}</span>
    </span>
  );
};
