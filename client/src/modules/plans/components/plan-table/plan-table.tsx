"use client";

import { DSTable, DSText } from "@/components/design-system";
import { useFormatDay } from "@/modules/stories/hooks/use-format-day";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { PlanSummary } from "../../typing/types/plan.type";
import { buildPlanPath } from "../../utils/plan-path.util";
import { PlanProgressBar } from "../plan-progress-bar/plan-progress-bar";
import { PlanStatusBadge } from "../plan-status-badge/plan-status-badge";
import styles from "./plan-table.module.scss";

interface Props {
  projectKey: string;
  plans: PlanSummary[];
}

export const PlanTable: FC<Props> = ({ projectKey, plans }) => {
  const { t } = useTranslation("plans");
  const formatDay = useFormatDay();

  return (
    <DSTable label={t("list.label")}>
      <caption className={styles.caption}>{t("list.label")}</caption>
      <thead>
        <tr>
          <th scope="col">{t("list.columns.name")}</th>
          <th scope="col">{t("list.columns.status")}</th>
          <th scope="col">{t("list.columns.progress")}</th>
          <th scope="col">{t("list.columns.targetDate")}</th>
          <th scope="col">{t("list.columns.environment")}</th>
          <th scope="col">{t("list.columns.items")}</th>
        </tr>
      </thead>
      <tbody>
        {plans.map((plan) => {
          return (
            <tr key={plan.id}>
              <td>
                <div className={styles.name}>
                  <Link href={buildPlanPath(projectKey, plan.id)}>{plan.name}</Link>
                  {plan.description !== null && (
                    <DSText size="xs" color="muted" component="span">
                      {plan.description}
                    </DSText>
                  )}
                </div>
              </td>
              <td>
                <PlanStatusBadge status={plan.status} />
              </td>
              <td>
                <PlanProgressBar counts={plan.counts} label={t("progress.label")} />
              </td>
              <td>
                {plan.targetDate === null ? (
                  <span className={styles.muted}>{t("list.noTargetDate")}</span>
                ) : (
                  formatDay(plan.targetDate)
                )}
              </td>
              <td>
                {plan.environmentName ?? (
                  <span className={styles.muted}>{t("list.anyEnvironment")}</span>
                )}
              </td>
              <td>{t("list.itemCount", { count: plan.itemCount })}</td>
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
