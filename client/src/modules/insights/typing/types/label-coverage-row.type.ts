import type { CaseShareCounts } from "./insights.type";

export interface LabelCoverageRow {
  key: string;
  name: string;
  counts: CaseShareCounts;
}
