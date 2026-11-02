import type { components } from "@/lib/api/openapi.type";

export type CaseDataKind = components["schemas"]["DataItemKind"];

export interface CaseDataValue {
  key: string;
  kind: CaseDataKind;
  value: string | null;
}

export interface CaseCriterion {
  code: string;
  text: string;
}

export interface CaseFile {
  key: string;
  fileName: string;
}

export interface CaseStep {
  order: number;
  action: string | null;
  expected: string | null;
  sharedStepKey?: string | null;
}

export interface CaseReferences {
  dataByKey: ReadonlyMap<string, CaseDataValue>;
  filesByKey: ReadonlyMap<string, CaseFile>;
  revealedValues: Readonly<Record<string, string>>;
  environmentName: string | null;
}

export interface CaseSecretReveal {
  canReveal: boolean;
  isRevealing: (key: string) => boolean;
  onReveal: (key: string) => void;
  onHide: (key: string) => void;
}

export type ReferenceKind = "data" | "file";

export type ReferencePart =
  { type: "text"; text: string } | { type: "reference"; kind: ReferenceKind; key: string };

export interface ReferencedKeys {
  dataKeys: string[];
  fileKeys: string[];
}
