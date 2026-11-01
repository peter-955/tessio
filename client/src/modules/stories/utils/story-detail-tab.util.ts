import { StoryDetailTab } from "../typing/enums/story-detail-tab.enum";
import type { StoryDetailSlots } from "../typing/types/story-detail-slots.type";

const STORY_DETAIL_TABS: readonly string[] = Object.values(StoryDetailTab);

const isStoryDetailTab = (value: string): value is StoryDetailTab => {
  return STORY_DETAIL_TABS.includes(value);
};

export const parseStoryDetailTab = (
  value: string | string[] | undefined,
  slots: StoryDetailSlots,
): StoryDetailTab => {
  const firstValue = Array.isArray(value) ? value[0] : value;

  if (firstValue === undefined || !isStoryDetailTab(firstValue)) {
    return StoryDetailTab.OVERVIEW;
  }

  if (firstValue === StoryDetailTab.OVERVIEW || slots[firstValue] !== undefined) {
    return firstValue;
  }

  return StoryDetailTab.OVERVIEW;
};
