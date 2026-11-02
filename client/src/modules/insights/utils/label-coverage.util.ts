import type { DSChartDatum } from "@/components/design-system";
import { CATEGORY_KEY } from "../typing/constants/insights.constant";
import type { LabelCoverageReport } from "../typing/types/insights.type";
import type { LabelCoverageRow } from "../typing/types/label-coverage-row.type";
import { toPercent } from "./insight-number.util";

export const listLabelCoverageRows = (
  report: LabelCoverageReport,
  unlabelledName: string,
): LabelCoverageRow[] => {
  const rows = report.labels.map((label): LabelCoverageRow => {
    return { key: label.labelId, name: label.name, counts: label.counts };
  });

  if (report.unlabelled.caseCount === 0) {
    return rows;
  }

  return [...rows, { key: "unlabelled", name: unlabelledName, counts: report.unlabelled }];
};

export const buildLabelCoverageData = (rows: LabelCoverageRow[]): DSChartDatum[] => {
  return rows.map((row) => {
    return {
      [CATEGORY_KEY]: row.name,
      ready: toPercent(row.counts.readyShare),
      passed: toPercent(row.counts.passedShare),
    };
  });
};
