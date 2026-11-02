import type { DSSelectOption } from "@/components/design-system";
import type { StorySummary } from "@/modules/stories/typing/types/story.type";
import type { PlanItem, PlanSuiteSummary } from "../typing/types/plan.type";

export const buildSuiteOptions = (
  suites: readonly PlanSuiteSummary[],
  items: readonly PlanItem[],
  formatArchived: (name: string) => string,
): DSSelectOption<string>[] => {
  const options = suites.map((suite): DSSelectOption<string> => {
    return {
      value: suite.id,
      label: suite.archivedAt === null ? suite.name : formatArchived(suite.name),
    };
  });
  const knownIds = new Set(
    options.map((option) => {
      return option.value;
    }),
  );
  const keptItems = items.flatMap((item): DSSelectOption<string>[] => {
    if (item.kind !== "suite" || item.suiteId === null || knownIds.has(item.suiteId)) {
      return [];
    }

    return [
      {
        value: item.suiteId,
        label: item.archivedAt === null ? item.name : formatArchived(item.name),
      },
    ];
  });

  return [...options, ...keptItems];
};

export const buildStoryOptions = (
  stories: readonly StorySummary[],
  items: readonly PlanItem[],
): DSSelectOption<string>[] => {
  const options = stories.map((story): DSSelectOption<string> => {
    return { value: story.id, label: `${story.jiraKey} · ${story.title}` };
  });
  const knownIds = new Set(
    options.map((option) => {
      return option.value;
    }),
  );
  const keptItems = items.flatMap((item): DSSelectOption<string>[] => {
    if (item.kind !== "story" || item.storyId === null || knownIds.has(item.storyId)) {
      return [];
    }

    return [
      {
        value: item.storyId,
        label: item.storyJiraKey === null ? item.name : `${item.storyJiraKey} · ${item.name}`,
      },
    ];
  });

  return [...options, ...keptItems];
};
