"use client";

import { DSButtonLink, DSErrorState, DSText } from "@/components/design-system";
import { useEffect, type FC } from "react";
import { useTranslation } from "react-i18next";
import styles from "./error-page.module.scss";
import { readErrorDigest } from "./utils/error-digest.util";

interface Props {
  error: unknown;
  onRetry: () => void;
}

export const ErrorPage: FC<Props> = ({ error, onRetry }) => {
  const { t } = useTranslation("errors");
  const digest = readErrorDigest(error);

  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main className={styles.page}>
      <div className={styles.content}>
        <DSErrorState
          title={t("boundary.title")}
          titleOrder={1}
          description={t("boundary.message")}
          retryLabel={t("boundary.retry")}
          onRetry={onRetry}
        />
        <DSButtonLink href="/" type="ghost">
          {t("boundary.homeLink")}
        </DSButtonLink>
        {digest !== null && (
          <DSText size="xs" color="muted">
            {t("boundary.reference", { digest })}
          </DSText>
        )}
      </div>
    </main>
  );
};
