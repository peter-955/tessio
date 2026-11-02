"use client";

import { DSBadge, DSBarChart, DSStack, DSTable, DSText } from "@/components/design-system";
import { buildRunPath } from "@/modules/runs/utils/run-path.util";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetTokenUsage } from "../../hooks/queries/use-get-token-usage";
import { useInsightFormatters } from "../../hooks/use-insight-formatters";
import { useLabelExecutor } from "../../hooks/use-label-executor";
import {
  CATEGORY_KEY,
  TOKEN_CHART_RUN_COUNT,
  TOKEN_TABLE_RUN_COUNT,
} from "../../typing/constants/insights.constant";
import type { InsightsRange } from "../../typing/types/insights-range.type";
import type { TokenRun, TokenUsage } from "../../typing/types/insights.type";
import { buildTokenChartData, describeTokenRunSource } from "../../utils/token-usage.util";
import { InsightPanel } from "../insight-panel/insight-panel";
import { InsightStatList } from "../insight-stat-list/insight-stat-list";
import styles from "./token-usage-card.module.scss";

interface Props {
  projectKey: string;
  range: InsightsRange;
}

export const TokenUsageCard: FC<Props> = ({ projectKey, range }) => {
  const { t } = useTranslation("insights");
  const labelExecutor = useLabelExecutor();
  const formatDate = useFormatDate();
  const { formatTokens } = useInsightFormatters();
  const { data, isPending, isError, isFetching, refetch } = useGetTokenUsage(projectKey, range);

  const formatOptionalTokens = (value: number | null): string => {
    return value === null ? t("noValue") : formatTokens(value);
  };

  const labelRun = (run: TokenRun): string => {
    return t("tokens.runLabel", {
      date: formatDate(run.startedAt),
      source: describeTokenRunSource(run),
    });
  };

  const renderContent = (usage: TokenUsage) => {
    return (
      <DSStack gap={4}>
        <InsightStatList
          stats={[
            {
              key: "total",
              label: t("tokens.total"),
              value: formatTokens(usage.totalTokens),
            },
            {
              key: "perRun",
              label: t("tokens.meanPerRun"),
              value: formatOptionalTokens(usage.meanTokensPerRun),
            },
            {
              key: "perCase",
              label: t("tokens.meanPerCase"),
              value: formatOptionalTokens(usage.meanTokensPerCase),
            },
            { key: "runs", label: t("tokens.runCount"), value: String(usage.runs.length) },
          ]}
        />
        <DSBarChart
          label={t("tokens.chart", { count: Math.min(usage.runs.length, TOKEN_CHART_RUN_COUNT) })}
          data={buildTokenChartData(usage.runs, labelRun)}
          xKey={CATEGORY_KEY}
          xLabel={t("tokens.columns.run")}
          series={[
            { key: "input", label: t("tokens.input"), color: "series1" },
            { key: "cacheWrite", label: t("tokens.cacheWrite"), color: "series2" },
            { key: "cacheRead", label: t("tokens.cacheRead"), color: "series3" },
            { key: "output", label: t("tokens.output"), color: "series4" },
          ]}
          valueFormatter={formatTokens}
          isStacked
        />
        <DSTable label={t("tokens.table")}>
          <thead>
            <tr>
              <th scope="col">{t("tokens.columns.run")}</th>
              <th scope="col">{t("tokens.columns.executor")}</th>
              <th scope="col">{t("tokens.columns.cases")}</th>
              <th scope="col">{t("tokens.columns.total")}</th>
              <th scope="col">{t("tokens.columns.perCase")}</th>
            </tr>
          </thead>
          <tbody>
            {usage.runs.slice(0, TOKEN_TABLE_RUN_COUNT).map((run) => {
              return (
                <tr key={run.runId}>
                  <td>
                    <span className={styles.run}>
                      <Link href={buildRunPath(projectKey, run.runId)}>
                        {describeTokenRunSource(run)}
                      </Link>
                      <DSText size="xs" color="muted" component="span">
                        {formatDate(run.startedAt)}
                      </DSText>
                      {run.isCut && <DSBadge color="yellow">{t("tokens.cut")}</DSBadge>}
                    </span>
                  </td>
                  <td>{labelExecutor(run.executor)}</td>
                  <td className={styles.numeric}>{run.caseCount}</td>
                  <td className={styles.numeric}>{formatTokens(run.totalTokens)}</td>
                  <td className={styles.numeric}>{formatOptionalTokens(run.tokensPerCase)}</td>
                </tr>
              );
            })}
          </tbody>
        </DSTable>
        {usage.runs.length > TOKEN_TABLE_RUN_COUNT && (
          <DSText size="xs" color="muted">
            {t("tokens.tableLimit", {
              shown: TOKEN_TABLE_RUN_COUNT,
              total: usage.runs.length,
            })}
          </DSText>
        )}
      </DSStack>
    );
  };

  return (
    <InsightPanel
      title={t("tokens.title")}
      description={t("tokens.description")}
      state={{ isPending, isError, isFetching, refetch }}
      isEmpty={data !== undefined && data.runs.length === 0}
      emptyTitle={t("tokens.emptyTitle")}
      emptyDescription={t("tokens.emptyDescription")}
      renderContent={() => {
        return data === undefined ? null : renderContent(data);
      }}
    />
  );
};
