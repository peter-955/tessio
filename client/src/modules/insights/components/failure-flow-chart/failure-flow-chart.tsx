"use client";

import { DSBarChart, DSCard, DSStack, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useInsightFormatters } from "../../hooks/use-insight-formatters";
import { CATEGORY_KEY } from "../../typing/constants/insights.constant";
import type { TrendPoint } from "../../typing/types/insights.type";
import { buildFailureData } from "../../utils/trend-chart.util";

interface Props {
  points: TrendPoint[];
  total: TrendPoint;
  axisLabel: string;
  labelPoint: (point: TrendPoint) => string;
}

export const FailureFlowChart: FC<Props> = ({ points, total, axisLabel, labelPoint }) => {
  const { t } = useTranslation("insights");
  const { formatDuration } = useInsightFormatters();

  return (
    <DSCard title={t("failures.title")}>
      <DSStack gap={2}>
        <DSText size="sm" color="muted">
          {t("failures.meanTimeToFix", { duration: formatDuration(total.meanTimeToFixSeconds) })}
        </DSText>
        <DSBarChart
          label={t("failures.title")}
          data={buildFailureData(points, labelPoint)}
          xKey={CATEGORY_KEY}
          xLabel={axisLabel}
          series={[
            { key: "opened", label: t("failures.opened"), color: "danger" },
            { key: "fixed", label: t("failures.fixed"), color: "success" },
          ]}
        />
      </DSStack>
    </DSCard>
  );
};
