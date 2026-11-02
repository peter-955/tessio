"use client";

import {
  DSBadge,
  DSCard,
  DSTabPanel,
  DSTable,
  DSTabs,
  DSText,
  type DSTabItem,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { FailureStatusBadge } from "@/modules/failures/components/failure-status-badge/failure-status-badge";
import { buildFailurePath } from "@/modules/failures/utils/failure-path.util";
import { buildStoryPath } from "@/modules/stories/utils/story-path.util";
import { buildTestCasePath } from "@/modules/test-cases/utils/test-case-path.util";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { EMPTY_VALUE, PLAN_CASE_FILTERS } from "../../typing/constants/plan.constant";
import type { PlanCaseFilter } from "../../typing/types/plan-case-status.type";
import type { PlanCase } from "../../typing/types/plan.type";
import { countPlanCasesByFilter, filterPlanCases } from "../../utils/plan-progress.util";
import { PlanCaseResult } from "../plan-case-result/plan-case-result";
import styles from "./plan-cases-card.module.scss";

interface Props {
  cases: PlanCase[];
}

export const PlanCasesCard: FC<Props> = ({ cases }) => {
  const { t } = useTranslation("plans");
  const project = useCurrentProject();
  const formatDate = useFormatDate();
  const [filter, setFilter] = useState<PlanCaseFilter>("all");
  const counts = countPlanCasesByFilter(cases);
  const visibleCases = filterPlanCases(cases, filter);
  const tabItems = PLAN_CASE_FILTERS.map((value): DSTabItem<PlanCaseFilter> => {
    return { value, label: t(`cases.filters.${value}`), count: counts[value] };
  });

  if (cases.length === 0) {
    return (
      <DSCard title={t("cases.title")}>
        <DSText size="sm" color="muted">
          {t("cases.noCases")}
        </DSText>
      </DSCard>
    );
  }

  return (
    <DSCard title={t("cases.title")}>
      <DSTabs
        items={tabItems}
        value={filter}
        onChange={setFilter}
        ariaLabel={t("cases.filterLabel")}
      >
        <DSTabPanel value={filter}>
          {visibleCases.length === 0 ? (
            <div className={styles.empty}>
              <DSText size="sm" color="muted">
                {t("cases.noMatch")}
              </DSText>
            </div>
          ) : (
            <DSTable label={t("cases.tableLabel")}>
              <caption className={styles.caption}>{t("cases.tableLabel")}</caption>
              <thead>
                <tr>
                  <th scope="col">{t("cases.columns.case")}</th>
                  <th scope="col">{t("cases.columns.story")}</th>
                  <th scope="col">{t("cases.columns.result")}</th>
                  <th scope="col">{t("cases.columns.recordedAt")}</th>
                  <th scope="col">{t("cases.columns.failure")}</th>
                </tr>
              </thead>
              <tbody>
                {visibleCases.map((planCase) => {
                  return (
                    <tr key={planCase.testCaseId}>
                      <td>
                        <div className={styles.case}>
                          <Link href={buildTestCasePath(project.key, planCase.code)}>
                            {`${planCase.code} · ${planCase.title}`}
                          </Link>
                          {planCase.status !== "ready" && (
                            <DSBadge>{t(`cases.caseStatus.${planCase.status}`)}</DSBadge>
                          )}
                          {planCase.isNeedingReview && (
                            <DSBadge color="orange">{t("cases.needsReview")}</DSBadge>
                          )}
                        </div>
                      </td>
                      <td>
                        <Link href={buildStoryPath(project.key, planCase.storyJiraKey)}>
                          {planCase.storyJiraKey}
                        </Link>
                      </td>
                      <td>
                        <PlanCaseResult planCase={planCase} />
                      </td>
                      <td>
                        {planCase.latestResult === null ? (
                          <span className={styles.muted}>{EMPTY_VALUE}</span>
                        ) : (
                          formatDate(planCase.latestResult.recordedAt)
                        )}
                      </td>
                      <td>
                        {planCase.activeFailureId === null ||
                        planCase.activeFailureStatus === null ? (
                          <span className={styles.muted}>{EMPTY_VALUE}</span>
                        ) : (
                          <Link href={buildFailurePath(project.key, planCase.activeFailureId)}>
                            <FailureStatusBadge status={planCase.activeFailureStatus} />
                          </Link>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </DSTable>
          )}
        </DSTabPanel>
      </DSTabs>
    </DSCard>
  );
};
