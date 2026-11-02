import type { DSSelectOption } from "@/components/design-system";
import { MAX_LABEL_NAME_LENGTH, MAX_LABELS_PER_CASE } from "../typing/constants/label.constant";
import type { Label } from "../typing/types/label.type";
import { findLabelByName } from "./label-name.util";

interface LabelFilterChoices {
  options: DSSelectOption<string>[];
  value: string[];
}

export const normalizeLabelNames = (names: readonly string[]): string[] => {
  const seenKeys = new Set<string>();
  const normalizedNames: string[] = [];

  for (const name of names) {
    const trimmedName = name.trim();
    const nameKey = trimmedName.toLocaleLowerCase();
    if (
      trimmedName === "" ||
      trimmedName.length > MAX_LABEL_NAME_LENGTH ||
      seenKeys.has(nameKey) ||
      normalizedNames.length >= MAX_LABELS_PER_CASE
    ) {
      continue;
    }

    seenKeys.add(nameKey);
    normalizedNames.push(trimmedName);
  }

  return normalizedNames;
};

export const parseLabelNames = (value: string | string[] | undefined): string[] => {
  if (value === undefined) {
    return [];
  }

  return normalizeLabelNames(Array.isArray(value) ? value : [value]);
};

export const buildLabelFilterChoices = (
  labels: readonly Label[],
  selectedNames: readonly string[],
): LabelFilterChoices => {
  const options = labels.map((label): DSSelectOption<string> => {
    return { value: label.name, label: label.name };
  });
  const value = selectedNames.map((name) => {
    const matchingLabel = findLabelByName(labels, name);
    if (matchingLabel !== undefined) {
      return matchingLabel.name;
    }

    options.push({ value: name, label: name });

    return name;
  });

  return { options, value };
};
