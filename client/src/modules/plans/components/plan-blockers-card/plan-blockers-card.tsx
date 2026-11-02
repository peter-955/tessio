"use client";

import { DSBadge, DSCard, DSText, DSTitle } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { FailureStatusBadge } from "@/modules/failures/components/failure-status-badge/failure-status-badge";
import { buildFailurePath } from "@/modules/failures/utils/failure-path.util";
import { buildStoryPath } from "@/modules/runs/utils/run-path.util";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { GAP_SEVERITY_COLORS } from "../../typing/constants/plan.constant";
import type { PlanFailure, PlanGap } from "../../typing/types/plan.type";
import styles from "./plan-blockers-card.module.scss";

interface Props {
  failures: PlanFailure[];
  gaps: PlanGap[];
}

export const PlanBlockersCard: FC<Props> = ({ failures, gaps }) => {
  const { t } = useTranslation("plans");
  const project = useCurrentProject();

  const formatGapAssignee = (gap: PlanGap): string => {
    if (gap.assigneeName !== null) {
      return gap.assigneeName;
    }

    if (gap.assigneeRole !== null) {
      return t("blockers.assignedToRole", { role: t(`blockers.roles.${gap.assigneeRole}`) });
    }

    return t("blockers.unassigned");
  };

  return (
    <DSCard title={t("blockers.title")}>
      <section className={styles.section}>
        <DSTitle order={3} type="section">
          {t("blockers.failures")}
        </DSTitle>
        {failures.length === 0 ? (
          <DSText size="sm" color="muted">
            {t("blockers.noFailures")}
          </DSText>
        ) : (
          <ul className={styles.list}>
            {failures.map((failure) => {
              return (
                <li key={failure.failureId} className={styles.entry}>
                  <Link href={buildFailurePath(project.key, failure.failureId)}>
                    {`${failure.code} · ${failure.title}`}
                  </Link>
                  <span className={styles.line}>
                    <FailureStatusBadge status={failure.status} />
                    <DSText size="xs" color="muted" component="span">
                      {`${failure.storyJiraKey} · ${failure.assigneeName ?? t("blockers.unassigned")}`}
                    </DSText>
                  </span>
                </li>
              );
            })}
          </ul>
        )}
      </section>
      <section className={styles.section}>
        <DSTitle order={3} type="section">
          {t("blockers.gaps")}
        </DSTitle>
        {gaps.length === 0 ? (
          <DSText size="sm" color="muted">
            {t("blockers.noGaps")}
          </DSText>
        ) : (
          <ul className={styles.list}>
            {gaps.map((gap) => {
              return (
                <li key={gap.gapId} className={styles.entry}>
                  <DSText size="sm" component="span">
                    {gap.question}
                  </DSText>
                  <span className={styles.line}>
                    <DSBadge color={GAP_SEVERITY_COLORS[gap.severity]}>
                      {t(`blockers.severity.${gap.severity}`)}
                    </DSBadge>
                    <Link href={buildStoryPath(project.key, gap.storyJiraKey, "gaps")}>
                      {gap.storyJiraKey}
                    </Link>
                    <DSText size="xs" color="muted" component="span">
                      {formatGapAssignee(gap)}
                    </DSText>
                  </span>
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </DSCard>
  );
};
