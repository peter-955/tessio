import type { AcceptanceCriterion } from "../typing/types/story.type";

export const sortCriteria = (criteria: AcceptanceCriterion[]): AcceptanceCriterion[] => {
  return [...criteria].sort((first, second) => {
    if (first.isRemoved !== second.isRemoved) {
      return first.isRemoved ? 1 : -1;
    }

    return first.position - second.position;
  });
};
