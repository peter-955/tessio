"use client";

import { DSButtonLink, DSEmptyState } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import styles from "./not-found.module.scss";

export const NotFoundPage: FC = () => {
  const { t } = useTranslation("errors");

  return (
    <main className={styles.page}>
      <DSEmptyState
        icon="alertCircle"
        title={t("notFound.title")}
        titleOrder={1}
        description={t("notFound.message")}
        action={<DSButtonLink href="/">{t("notFound.backLink")}</DSButtonLink>}
      />
    </main>
  );
};
