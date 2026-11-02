import type { DSSelectOption } from "@/components/design-system";
import type { CaseLabel, Label } from "../typing/types/label.type";

export const buildLabelOptions = (
  labels: readonly Label[],
  selectedLabels: readonly CaseLabel[],
): DSSelectOption<string>[] => {
  const knownIds = new Set(labels.map((label) => label.id));
  const missingLabels = selectedLabels.filter((label) => !knownIds.has(label.id));

  return [...labels, ...missingLabels].map((label): DSSelectOption<string> => {
    return { value: label.id, label: label.name };
  });
};

export const checkHasSameLabelIds = (
  labelIds: readonly string[],
  labels: readonly CaseLabel[],
): boolean => {
  const currentIds = new Set(labels.map((label) => label.id));

  return labelIds.length === currentIds.size && labelIds.every((id) => currentIds.has(id));
};
