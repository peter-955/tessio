"use client";

import { DSBadge, DSText } from "@/components/design-system";
import type { SuspectedCause as SuspectedCauseValue } from "@/shared/typing/types/test-run.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import styles from "./suspected-cause.module.scss";

interface Props {
  cause: SuspectedCauseValue;
  reason: string | null;
}

export const SuspectedCause: FC<Props> = ({ cause, reason }) => {
  const { t } = useTranslation("diagnosis");

  return (
    <div className={styles.cause}>
      <span className={styles.label}>
        <DSText size="sm" weight="medium" component="span">
          {t("suspectedCause")}
        </DSText>
        <DSBadge color={cause === "app_bug" ? "red" : "gray"} hasDot>
          {t(`cause.${cause}`)}
        </DSBadge>
      </span>
      {reason !== null && reason !== "" && (
        <DSText size="sm" className={styles.reason}>
          {reason}
        </DSText>
      )}
    </div>
  );
};
