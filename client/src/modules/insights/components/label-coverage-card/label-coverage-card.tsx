"use client";

import { DSBarChart, DSStack, DSTable } from "@/components/design-system";
import { LabelChip } from "@/modules/labels/components/label-chip/label-chip";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetLabelCoverage } from "../../hooks/queries/use-get-label-coverage";
import { useInsightFormatters } from "../../hooks/use-insight-formatters";
import { CATEGORY_KEY } from "../../typing/constants/insights.constant";
import type { LabelCoverageReport } from "../../typing/types/insights.type";
import { buildLabelCoverageData, listLabelCoverageRows } from "../../utils/label-coverage.util";
import { InsightPanel } from "../insight-panel/insight-panel";
import styles from "./label-coverage-card.module.scss";

interface Props {
  projectKey: string;
}

const BAR_ROW_HEIGHT = 40;

const BAR_CHART_PADDING = 80;

export const LabelCoverageCard: FC<Props> = ({ projectKey }) => {
  const { t } = useTranslation("insights");
  const { formatPercent, formatShare } = useInsightFormatters();
  const { data, isPending, isError, isFetching, refetch } = useGetLabelCoverage(projectKey);

  const renderContent = (report: LabelCoverageReport) => {
    const rows = listLabelCoverageRows(report, t("labels.unlabelled"));
    const labelsById = new Map(
      report.labels.map((label) => {
        return [label.labelId, label];
      }),
    );

    return (
      <DSStack gap={4}>
        <DSBarChart
          label={t("labels.chart")}
          data={buildLabelCoverageData(rows)}
          xKey={CATEGORY_KEY}
          xLabel={t("labels.columns.label")}
          series={[
            { key: "ready", label: t("labels.readyShare"), color: "series1" },
            { key: "passed", label: t("labels.passedShare"), color: "success" },
          ]}
          height={rows.length * BAR_ROW_HEIGHT + BAR_CHART_PADDING}
          valueFormatter={formatPercent}
          isHorizontal
        />
        <DSTable label={t("labels.table")}>
          <thead>
            <tr>
              <th scope="col">{t("labels.columns.label")}</th>
              <th scope="col">{t("labels.columns.cases")}</th>
              <th scope="col">{t("labels.columns.ready")}</th>
              <th scope="col">{t("labels.columns.passed")}</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const label = labelsById.get(row.key);
              return (
                <tr key={row.key}>
                  <th scope="row" className={styles.name}>
                    {label === undefined ? (
                      row.name
                    ) : (
                      <LabelChip name={label.name} color={label.color} />
                    )}
                  </th>
                  <td className={styles.numeric}>{row.counts.caseCount}</td>
                  <td className={styles.numeric}>
                    {t("labels.countWithShare", {
                      count: row.counts.readyCount,
                      share: formatShare(row.counts.readyShare),
                    })}
                  </td>
                  <td className={styles.numeric}>
                    {t("labels.countWithShare", {
                      count: row.counts.passedCount,
                      share: formatShare(row.counts.passedShare),
                    })}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </DSTable>
      </DSStack>
    );
  };

  return (
    <InsightPanel
      title={t("labels.title")}
      description={t("labels.description")}
      state={{ isPending, isError, isFetching, refetch }}
      isEmpty={data !== undefined && data.total.caseCount === 0}
      emptyTitle={t("labels.emptyTitle")}
      emptyDescription={t("labels.emptyDescription")}
      renderContent={() => {
        return data === undefined ? null : renderContent(data);
      }}
    />
  );
};
