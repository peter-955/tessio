"use client";

import { DSAlert, DSCard, DSPageHeader } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { FailingCasesCard } from "./components/failing-cases-card/failing-cases-card";
import { FlakyCasesCard } from "./components/flaky-cases-card/flaky-cases-card";
import { InsightsFilters } from "./components/insights-filters/insights-filters";
import { LabelCoverageCard } from "./components/label-coverage-card/label-coverage-card";
import { SprintCoverageCard } from "./components/sprint-coverage-card/sprint-coverage-card";
import { TokenUsageCard } from "./components/token-usage-card/token-usage-card";
import { TrendsSection } from "./components/trends-section/trends-section";
import { useInsightsFilters } from "./hooks/use-insights-filters";
import styles from "./insights.module.scss";
import { MAX_RANGE_DAYS } from "./typing/constants/insights.constant";
import { findRangeProblem } from "./utils/insights-range.util";

export const InsightsPage: FC = () => {
  const { t } = useTranslation("insights");
  const project = useCurrentProject();
  const { range, groupBy, sprintId, changeFrom, changeTo, changeSprint, changeGroupBy } =
    useInsightsFilters();
  const rangeProblem = findRangeProblem(range);

  return (
    <>
      <DSPageHeader title={t("page.title")} description={t("page.description")} />
      <div className={styles.page}>
        <DSCard>
          <InsightsFilters
            projectKey={project.key}
            range={range}
            groupBy={groupBy}
            sprintId={sprintId}
            onFromChange={changeFrom}
            onToChange={changeTo}
            onSprintChange={changeSprint}
            onGroupByChange={changeGroupBy}
          />
        </DSCard>
        {rangeProblem === null ? (
          <>
            <TrendsSection projectKey={project.key} range={range} groupBy={groupBy} />
            <div className={styles.grid}>
              <FailingCasesCard projectKey={project.key} range={range} />
              <FlakyCasesCard projectKey={project.key} />
            </div>
            <LabelCoverageCard projectKey={project.key} />
            <SprintCoverageCard projectKey={project.key} range={range} />
            <TokenUsageCard projectKey={project.key} range={range} />
          </>
        ) : (
          <DSAlert color="warning" title={t("rangeProblem.title")}>
            {t(`rangeProblem.${rangeProblem}`, { maxDays: MAX_RANGE_DAYS })}
          </DSAlert>
        )}
      </div>
    </>
  );
};
