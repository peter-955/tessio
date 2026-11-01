import {
  DS_MAX_REFERENCE_SUGGESTIONS,
  DS_REFERENCE_CLOSING,
  DS_REFERENCE_QUERY_PATTERN,
} from "./step-editor.constant";
import type {
  DSReferenceInsertion,
  DSReferenceKind,
  DSReferenceQuery,
  DSReferenceSuggestion,
} from "./step-editor.type";

const isReferenceKind = (value: string | undefined): value is DSReferenceKind => {
  return value === "data" || value === "file";
};

export const findReferenceQuery = (text: string, caret: number): DSReferenceQuery | null => {
  const match = DS_REFERENCE_QUERY_PATTERN.exec(text.slice(0, caret));
  const kind = match?.[1];

  if (match === null || !isReferenceKind(kind)) {
    return null;
  }

  return { kind, prefix: match[2] ?? "", start: match.index };
};

export const insertReference = (
  text: string,
  query: DSReferenceQuery,
  key: string,
  caret: number,
): DSReferenceInsertion => {
  const before = text.slice(0, query.start);
  const after = text.slice(caret);
  const token = `{{${query.kind}.${key}`;
  const remainder = after.startsWith(DS_REFERENCE_CLOSING)
    ? after.slice(DS_REFERENCE_CLOSING.length)
    : after;
  const completedText = `${before}${token}${DS_REFERENCE_CLOSING}`;

  return { text: `${completedText}${remainder}`, caret: completedText.length };
};

export const filterSuggestions = (
  suggestions: readonly DSReferenceSuggestion[],
  query: DSReferenceQuery,
): DSReferenceSuggestion[] => {
  const prefix = query.prefix.toLowerCase();
  const sameKind = suggestions.filter((suggestion) => {
    return suggestion.kind === query.kind;
  });
  const startingWith = sameKind.filter((suggestion) => {
    return suggestion.key.toLowerCase().startsWith(prefix);
  });
  const containing = sameKind.filter((suggestion) => {
    const key = suggestion.key.toLowerCase();

    return !key.startsWith(prefix) && key.includes(prefix);
  });

  return [...startingWith, ...containing].slice(0, DS_MAX_REFERENCE_SUGGESTIONS);
};
