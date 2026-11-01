"use client";

import { DSErrorState, DSLoader } from "@/components/design-system";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import styles from "./auth-step-gate.module.scss";

interface Props {
  isReady: boolean;
  isLoadFailed: boolean;
  isRetrying: boolean;
  onRetry: () => void;
  children: ReactNode;
}

export const AuthStepGate: FC<Props> = ({
  isReady,
  isLoadFailed,
  isRetrying,
  onRetry,
  children,
}) => {
  const { t } = useTranslation("auth");

  if (isLoadFailed) {
    return (
      <DSErrorState
        title={t("session.loadFailed")}
        retryLabel={t("session.retry")}
        onRetry={onRetry}
        isRetrying={isRetrying}
      />
    );
  }

  if (!isReady) {
    return (
      <div className={styles.loader}>
        <DSLoader size="md" />
      </div>
    );
  }

  return children;
};
