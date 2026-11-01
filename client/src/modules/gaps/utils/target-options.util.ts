import type { DSSelectOption } from "@/components/design-system";
import type { AcceptanceCriterion } from "@/modules/stories/typing/types/story.type";
import { MAX_TARGET_LABEL_LENGTH, TARGET_LABEL_ELLIPSIS } from "../typing/constants/gap.constant";

export const truncateLabel = (label: string, maximumLength = MAX_TARGET_LABEL_LENGTH): string => {
  if (label.length <= maximumLength) {
    return label;
  }

  return `${label.slice(0, maximumLength - TARGET_LABEL_ELLIPSIS.length).trimEnd()}${TARGET_LABEL_ELLIPSIS}`;
};

export const buildCriterionOptions = (
  criteria: AcceptanceCriterion[],
): DSSelectOption<string>[] => {
  return criteria
    .filter((criterion) => {
      return !criterion.isRemoved;
    })
    .map((criterion): DSSelectOption<string> => {
      return {
        value: criterion.code,
        label: truncateLabel(`${criterion.code} · ${criterion.text}`),
      };
    });
};

export const buildTestCaseOption = (code: string, title: string): DSSelectOption<string> => {
  return { value: code, label: truncateLabel(`${code} · ${title}`) };
};
