"use client";

import { DSBarChart } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetSprintCoverage } from "../../hooks/queries/use-get-sprint-coverage";
import { CATEGORY_KEY } from "../../typing/constants/insights.constant";
import type { InsightsRange } from "../../typing/types/insights-range.type";
import {
  buildSprintCoverageData,
  checkSprintCoverageHasCriteria,
} from "../../utils/sprint-coverage.util";
import { InsightPanel } from "../insight-panel/insight-panel";

interface Props {
  projectKey: string;
  range: InsightsRange;
}

export const SprintCoverageCard: FC<Props> = ({ projectKey, range }) => {
  const { t } = useTranslation("insights");
  const { data, isPending, isError, isFetching, refetch } = useGetSprintCoverage(projectKey, range);

  return (
    <InsightPanel
      title={t("sprintCoverage.title")}
      description={t("sprintCoverage.description")}
      state={{ isPending, isError, isFetching, refetch }}
      isEmpty={data !== undefined && !checkSprintCoverageHasCriteria(data)}
      emptyTitle={t("sprintCoverage.emptyTitle")}
      emptyDescription={t("sprintCoverage.emptyDescription")}
      renderContent={() => {
        return data === undefined ? null : (
          <DSBarChart
            label={t("sprintCoverage.title")}
            data={buildSprintCoverageData(data)}
            xKey={CATEGORY_KEY}
            xLabel={t("axis.sprint")}
            series={[
              { key: "passed", label: t("sprintCoverage.passed"), color: "success" },
              { key: "failed", label: t("sprintCoverage.failed"), color: "danger" },
              { key: "blocked", label: t("sprintCoverage.blocked"), color: "warning" },
              { key: "notRun", label: t("sprintCoverage.notRun"), color: "series1" },
              { key: "uncovered", label: t("sprintCoverage.uncovered"), color: "muted" },
            ]}
            isStacked
          />
        );
      }}
    />
  );
};
