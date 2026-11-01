import type { GapDataScope, GapSeverity, GapTargetType, GapType } from "./gap.type";

export interface RaiseGapInput {
  type: GapType;
  severity: GapSeverity;
  targetType: GapTargetType;
  targetRef: string | null;
  dataScope: GapDataScope | null;
  question: string;
  assigneeId: string | null;
}

export type RaiseGapValues = Omit<RaiseGapInput, "type"> & { type: GapType | null };
