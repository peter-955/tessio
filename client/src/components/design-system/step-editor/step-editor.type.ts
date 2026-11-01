export interface DSStepEditorStep {
  id: string;
  action: string;
  expected: string;
}

export type DSReferenceKind = "data" | "file";

export interface DSReferenceSuggestion {
  kind: DSReferenceKind;
  key: string;
}

export interface DSReferenceQuery {
  kind: DSReferenceKind;
  prefix: string;
  start: number;
}

export interface DSReferenceInsertion {
  text: string;
  caret: number;
}

export interface DSStepEditorLabels {
  step: (position: number) => string;
  action: string;
  expected: string;
  addStep: string;
  moveUp: string;
  moveDown: string;
  remove: string;
  stepActions: (position: number) => string;
  suggestions: string;
  noSuggestions: string;
}
