import type {
  CriterionDraft,
  StoryEditorValues,
  StoryRequest,
} from "../typing/types/story-editor.type";
import type { StoryDetail } from "../typing/types/story.type";

export const createCriterionDraft = (text = ""): CriterionDraft => {
  return { id: crypto.randomUUID(), text };
};

export const buildStoryEditorValues = (story: StoryDetail | null): StoryEditorValues => {
  if (story === null) {
    return { title: "", description: "", criteria: [createCriterionDraft()] };
  }

  return {
    title: story.title,
    description: story.descriptionText ?? "",
    criteria: story.criteria
      .filter((criterion) => {
        return !criterion.isRemoved;
      })
      .map((criterion) => {
        return createCriterionDraft(criterion.text);
      }),
  };
};

export const buildStoryRequest = (values: StoryEditorValues): StoryRequest => {
  const description = values.description.trim();

  return {
    title: values.title.trim(),
    description: description === "" ? null : description,
    criteria: values.criteria
      .map((criterion) => {
        return criterion.text.trim();
      })
      .filter((text) => {
        return text !== "";
      }),
  };
};

export const moveCriterion = (
  criteria: readonly CriterionDraft[],
  index: number,
  offset: number,
): CriterionDraft[] => {
  const target = index + offset;
  if (target < 0 || target >= criteria.length) {
    return [...criteria];
  }

  const moved = [...criteria];
  const [criterion] = moved.splice(index, 1);
  if (criterion !== undefined) {
    moved.splice(target, 0, criterion);
  }

  return moved;
};
