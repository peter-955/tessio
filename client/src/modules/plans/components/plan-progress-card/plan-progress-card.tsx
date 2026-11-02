"use client";

import { DSBadge, DSCard, DSText } from "@/components/design-system";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { PLAN_CASE_STATUS_COLORS, PLAN_CASE_STATUSES } from "../../typing/constants/plan.constant";
import type { PlanDetail } from "../../typing/types/plan.type";
import {
  calculatePassedPercent,
  readStatusCount,
  selectPlanProgressWindow,
} from "../../utils/plan-progress.util";
import { PlanProgressBar } from "../plan-progress-bar/plan-progress-bar";
import styles from "./plan-progress-card.module.scss";

interface Props {
  plan: PlanDetail;
}

export const PlanProgressCard: FC<Props> = ({ plan }) => {
  const { t } = useTranslation("plans");
  const formatDate = useFormatDate();
  const { counts } = plan.progress;

  const progressWindow = selectPlanProgressWindow(plan);
  const windowText =
    progressWindow === "open"
      ? t("progress.since", { date: formatDate(plan.createdAt) })
      : t(`progress.${progressWindow}`);

  return (
    <DSCard title={t("progress.title")}>
      <div className={styles.headline}>
        <span className={styles.percent}>
          {t("progress.passedPercent", { percent: calculatePassedPercent(counts) })}
        </span>
        <DSText size="xs" color="muted" component="span">
          {windowText}
        </DSText>
      </div>
      <PlanProgressBar counts={counts} label={t("progress.label")} size="lg" />
      <div className={styles.legend}>
        {PLAN_CASE_STATUSES.map((status) => {
          return (
            <DSBadge key={status} color={PLAN_CASE_STATUS_COLORS[status]}>
              {t("progress.segment", {
                status: t(`caseStatus.${status}`),
                count: readStatusCount(counts, status),
              })}
            </DSBadge>
          );
        })}
      </div>
    </DSCard>
  );
};
