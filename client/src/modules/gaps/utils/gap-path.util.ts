import { STORY_DETAIL_TAB_PARAMETER } from "@/modules/stories/typing/constants/story.constant";
import { buildStoryPath } from "@/modules/stories/utils/story-path.util";
import { GAPS_TAB_PARAMETER_VALUE } from "../typing/constants/gap.constant";

export const buildStoryGapsHref = (projectKey: string, jiraKey: string): string => {
  return `${buildStoryPath(projectKey, jiraKey)}?${STORY_DETAIL_TAB_PARAMETER}=${GAPS_TAB_PARAMETER_VALUE}`;
};
