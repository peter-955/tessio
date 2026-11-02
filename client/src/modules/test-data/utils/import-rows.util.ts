import type { ImportRow } from "../typing/types/import-row.type";
import type { ImportPreviewItem } from "../typing/types/import.type";

export const isImportRowLocked = (
  row: Pick<ImportRow, "suggestedKind">,
  canEditSecrets: boolean,
): boolean => {
  return row.suggestedKind === "secret" && !canEditSecrets;
};

export const buildImportRows = (
  items: readonly ImportPreviewItem[],
  canEditSecrets: boolean,
): ImportRow[] => {
  return items.map((item) => {
    const isLocked = isImportRowLocked({ suggestedKind: item.kind }, canEditSecrets);

    return {
      key: item.key,
      kind: item.kind,
      suggestedKind: item.kind,
      value: item.value,
      description: item.description,
      action: item.action,
      isIncluded: !isLocked && item.action !== "unchanged",
    };
  });
};
