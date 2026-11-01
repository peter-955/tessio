"use client";

import { DSStack, DSText, DSTitle } from "@/components/design-system";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import type { CoverageCounts } from "../../typing/types/dashboard.type";
import { buildCoverageSegments } from "../../utils/coverage.util";
import styles from "./coverage-meter.module.scss";

interface Props {
  coverage: CoverageCounts;
}

export const CoverageMeter: FC<Props> = ({ coverage }) => {
  const { t } = useTranslation("dashboard");
  const segments = buildCoverageSegments(coverage);

  const renderContent = (): ReactNode => {
    if (coverage.criterionCount === 0) {
      return <DSText color="muted">{t("coverage.empty")}</DSText>;
    }

    return (
      <>
        <DSText>
          {t("coverage.summary", {
            covered: coverage.coveredCount,
            total: coverage.criterionCount,
          })}
        </DSText>
        <div
          role="img"
          aria-label={t("coverage.barLabel", {
            passed: coverage.passedCount,
            failed: coverage.failedCount,
            blocked: coverage.blockedCount,
            notRun: coverage.notRunCount,
            uncovered: coverage.uncoveredCount,
          })}
          className={styles.bar}
        >
          {segments.map((segment) => {
            return (
              <div
                key={segment.kind}
                className={`${styles.segment} ${styles[segment.kind]}`}
                style={{ flexGrow: segment.count }}
              />
            );
          })}
        </div>
        <ul className={styles.legend}>
          {segments.map((segment) => {
            return (
              <li key={segment.kind} className={styles.legendItem}>
                <span aria-hidden className={`${styles.swatch} ${styles[segment.kind]}`} />
                <span>{t(`coverage.segments.${segment.kind}`)}</span>
                <span className={styles.legendCount}>{segment.count}</span>
              </li>
            );
          })}
        </ul>
      </>
    );
  };

  return (
    <DSStack gap={3}>
      <DSTitle order={3} type="section">
        {t("coverage.title")}
      </DSTitle>
      {renderContent()}
    </DSStack>
  );
};
