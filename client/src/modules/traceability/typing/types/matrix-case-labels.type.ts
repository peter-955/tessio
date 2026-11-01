import type { TestCaseStatus } from "@/modules/test-cases/typing/types/test-case.type";

export type NotReadyCaseStatus = Extract<TestCaseStatus, "draft" | "in_review">;

export interface MatrixCaseLabels {
  notReady: Record<NotReadyCaseStatus, string>;
  needsReview: string;
}
