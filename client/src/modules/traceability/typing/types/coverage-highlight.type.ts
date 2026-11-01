export type CoverageHighlightKind = "failing" | "blocked" | "uncovered" | "allPassing";

export interface CoverageHighlight {
  kind: CoverageHighlightKind;
  count: number;
}
