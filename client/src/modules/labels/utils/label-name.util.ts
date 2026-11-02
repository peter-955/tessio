import { MAX_LABEL_NAME_LENGTH } from "../typing/constants/label.constant";
import type { LabelNameError } from "../typing/types/label-name-error.type";

interface NamedLabel {
  id: string;
  name: string;
}

const toNameKey = (name: string): string => {
  return name.trim().toLocaleLowerCase();
};

export const findLabelByName = <T extends NamedLabel>(
  labels: readonly T[],
  name: string,
): T | undefined => {
  const nameKey = toNameKey(name);

  return labels.find((label) => toNameKey(label.name) === nameKey);
};

export const findLabelNameError = (
  name: string,
  labels: readonly NamedLabel[],
  editedLabelId: string | null = null,
): LabelNameError | null => {
  const trimmedName = name.trim();
  if (trimmedName === "") {
    return "required";
  }

  if (trimmedName.length > MAX_LABEL_NAME_LENGTH) {
    return "tooLong";
  }

  const sameNameLabel = findLabelByName(labels, trimmedName);

  return sameNameLabel !== undefined && sameNameLabel.id !== editedLabelId ? "alreadyUsed" : null;
};
