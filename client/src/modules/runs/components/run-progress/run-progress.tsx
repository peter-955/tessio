"use client";

import { DSBadge, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import styles from "./run-progress.module.scss";

interface Props {
  reportedCount: number;
  totalCount: number;
}

export const RunProgress: FC<Props> = ({ reportedCount, totalCount }) => {
  const { t } = useTranslation("runs");

  return (
    <div className={styles.progress} aria-live="polite">
      <DSBadge color="tessio" hasDot>
        {t("detail.live")}
      </DSBadge>
      <DSText size="sm" component="span">
        {t("detail.progress", { reported: reportedCount, total: totalCount })}
      </DSText>
      <DSText size="xs" color="muted" component="span">
        {t("report.notReady")}
      </DSText>
    </div>
  );
};
