"use client";

import { useFormatDay } from "@/modules/stories/hooks/use-format-day";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetInsightTrends } from "../../hooks/queries/use-get-insight-trends";
import type { InsightsRange } from "../../typing/types/insights-range.type";
import type { TrendGrouping, TrendPoint } from "../../typing/types/insights.type";
import { checkTrendsHaveData, labelTrendPoint } from "../../utils/trend-chart.util";
import { ExecutorRunsChart } from "../executor-runs-chart/executor-runs-chart";
import { FailureFlowChart } from "../failure-flow-chart/failure-flow-chart";
import { GapAgeChart } from "../gap-age-chart/gap-age-chart";
import { InsightPanel } from "../insight-panel/insight-panel";
import { PassRateChart } from "../pass-rate-chart/pass-rate-chart";
import { TrendSummary } from "../trend-summary/trend-summary";
import styles from "./trends-section.module.scss";

interface Props {
  projectKey: string;
  range: InsightsRange;
  groupBy: TrendGrouping;
}

export const TrendsSection: FC<Props> = ({ projectKey, range, groupBy }) => {
  const { t } = useTranslation("insights");
  const formatDay = useFormatDay();
  const { data, isPending, isError, isFetching, refetch } = useGetInsightTrends(
    projectKey,
    range,
    groupBy,
  );
  const hasData = data !== undefined && checkTrendsHaveData(data);
  const axisLabel = t(`axis.${groupBy}`);

  const labelPoint = (point: TrendPoint): string => {
    return labelTrendPoint(point, formatDay);
  };

  return (
    <>
      <InsightPanel
        title={t("summary.title")}
        description={
          data === undefined
            ? undefined
            : t("summary.range", {
                from: formatDay(data.firstDay),
                to: formatDay(data.lastDay),
              })
        }
        state={{ isPending, isError, isFetching, refetch }}
        isEmpty={!hasData}
        emptyTitle={t(groupBy === "sprint" ? "summary.emptySprintTitle" : "summary.emptyTitle")}
        emptyDescription={t("summary.emptyDescription")}
        renderContent={() => {
          return data === undefined ? null : <TrendSummary total={data.total} />;
        }}
      />
      {data !== undefined && hasData && (
        <div className={styles.grid}>
          <PassRateChart points={data.points} axisLabel={axisLabel} labelPoint={labelPoint} />
          <ExecutorRunsChart
            points={data.points}
            executors={data.executors}
            axisLabel={axisLabel}
            labelPoint={labelPoint}
          />
          <FailureFlowChart
            points={data.points}
            total={data.total}
            axisLabel={axisLabel}
            labelPoint={labelPoint}
          />
          <GapAgeChart
            points={data.points}
            total={data.total}
            axisLabel={axisLabel}
            labelPoint={labelPoint}
          />
        </div>
      )}
    </>
  );
};
