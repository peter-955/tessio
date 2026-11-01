import type { AcceptanceCriterion } from "@/modules/stories/typing/types/story.type";
import type { CriterionOptionSource } from "../typing/types/criterion-option-source.type";
import type { LinkedCriterion } from "../typing/types/test-case.type";

export const mergeCriterionOptionSources = (
  storyCriteria: readonly AcceptanceCriterion[],
  linkedCriteria: readonly LinkedCriterion[],
  selectedIds: readonly string[],
): CriterionOptionSource[] => {
  const selected = new Set(selectedIds);
  const sources = new Map<string, CriterionOptionSource>();

  for (const criterion of storyCriteria) {
    if (!criterion.isRemoved || selected.has(criterion.id)) {
      sources.set(criterion.id, criterion);
    }
  }

  for (const criterion of linkedCriteria) {
    if (!sources.has(criterion.id) && selected.has(criterion.id)) {
      sources.set(criterion.id, criterion);
    }
  }

  return [...sources.values()];
};
