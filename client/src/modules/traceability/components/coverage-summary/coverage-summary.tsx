"use client";

import { DSBadge, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { CoverageCount } from "../../typing/types/traceability.type";
import styles from "./coverage-summary.module.scss";

interface Props {
  coverage: CoverageCount;
}

export const CoverageSummary: FC<Props> = ({ coverage }) => {
  const { t } = useTranslation("traceability");

  return (
    <div className={styles.root}>
      <DSText weight="medium">
        {t("coverage.covered", {
          covered: coverage.coveredCount,
          total: coverage.criterionCount,
        })}
      </DSText>
      <div className={styles.counts}>
        {coverage.passedCount > 0 && (
          <DSBadge color="green">{t("coverage.passed", { count: coverage.passedCount })}</DSBadge>
        )}
        {coverage.failedCount > 0 && (
          <DSBadge color="red">{t("coverage.failed", { count: coverage.failedCount })}</DSBadge>
        )}
        {coverage.blockedCount > 0 && (
          <DSBadge color="yellow">
            {t("coverage.blocked", { count: coverage.blockedCount })}
          </DSBadge>
        )}
        {coverage.notRunCount > 0 && (
          <DSBadge color="gray">{t("coverage.notRun", { count: coverage.notRunCount })}</DSBadge>
        )}
      </div>
    </div>
  );
};
