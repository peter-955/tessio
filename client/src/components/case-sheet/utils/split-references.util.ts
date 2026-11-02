import { REFERENCE_PATTERN } from "../typing/constants/case-sheet.constant";
import type {
  CaseStep,
  ReferenceKind,
  ReferencePart,
  ReferencedKeys,
} from "../typing/types/case-sheet.type";

const readReferenceKind = (kind: string): ReferenceKind => {
  return kind === "file" ? "file" : "data";
};

export const splitReferences = (text: string): ReferencePart[] => {
  const parts: ReferencePart[] = [];
  let textStart = 0;

  for (const match of text.matchAll(REFERENCE_PATTERN)) {
    const [reference, kind, key] = match;
    if (match.index > textStart) {
      parts.push({ type: "text", text: text.slice(textStart, match.index) });
    }
    parts.push({ type: "reference", kind: readReferenceKind(kind), key });
    textStart = match.index + reference.length;
  }

  if (textStart < text.length) {
    parts.push({ type: "text", text: text.slice(textStart) });
  }

  return parts;
};

export const listReferencedKeys = (
  texts: readonly (string | null)[],
  steps: readonly CaseStep[],
): ReferencedKeys => {
  const dataKeys = new Set<string>();
  const fileKeys = new Set<string>();
  const allTexts = [
    ...texts,
    ...steps.flatMap((step) => {
      return [step.action, step.expected];
    }),
  ];

  for (const text of allTexts) {
    for (const part of splitReferences(text ?? "")) {
      if (part.type === "reference") {
        (part.kind === "data" ? dataKeys : fileKeys).add(part.key);
      }
    }
  }

  return { dataKeys: [...dataKeys], fileKeys: [...fileKeys] };
};
