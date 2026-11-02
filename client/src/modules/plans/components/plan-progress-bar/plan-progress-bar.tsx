"use client";

import { DSProgress, DSText, type DSProgressSection } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { PLAN_CASE_STATUS_COLORS } from "../../typing/constants/plan.constant";
import type { PlanProgressCounts } from "../../typing/types/plan.type";
import { buildProgressSegments } from "../../utils/plan-progress.util";
import styles from "./plan-progress-bar.module.scss";

interface Props {
  counts: PlanProgressCounts;
  label: string;
  size?: "sm" | "md" | "lg";
}

export const PlanProgressBar: FC<Props> = ({ counts, label, size = "sm" }) => {
  const { t } = useTranslation("plans");
  const sections = buildProgressSegments(counts).map((segment): DSProgressSection => {
    return {
      key: segment.status,
      value: segment.percent,
      color: PLAN_CASE_STATUS_COLORS[segment.status],
      label: t("progress.segment", {
        status: t(`caseStatus.${segment.status}`),
        count: segment.count,
      }),
    };
  });

  return (
    <div className={styles.progress}>
      <DSProgress label={label} sections={sections} size={size} />
      <DSText size="xs" color="muted" component="span">
        {counts.total === 0
          ? t("progress.noCases")
          : t("progress.summary", { passed: counts.passed, total: counts.total })}
      </DSText>
    </div>
  );
};
