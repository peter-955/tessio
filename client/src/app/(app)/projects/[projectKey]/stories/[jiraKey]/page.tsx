import { StoryGaps } from "@/modules/gaps/components/story-gaps/story-gaps";
import { NewManualRunButtonLink } from "@/modules/manual-run/components/new-manual-run-button-link/new-manual-run-button-link";
import { StoryRuns } from "@/modules/runs/components/story-runs/story-runs";
import { StoryDetailPage } from "@/modules/stories/story-detail";
import { StoryDetailTab } from "@/modules/stories/typing/enums/story-detail-tab.enum";
import type { StoryDetailSlots } from "@/modules/stories/typing/types/story-detail-slots.type";
import { parseStoryDetailTab } from "@/modules/stories/utils/story-detail-tab.util";
import { StoryTestCases } from "@/modules/test-cases/story-test-cases";
import { StoryTraceability } from "@/modules/traceability/story-traceability";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Story" };

const StoryRoute: FC<PageProps<"/projects/[projectKey]/stories/[jiraKey]">> = async ({
  params,
  searchParams,
}) => {
  const { jiraKey } = await params;
  const { tab } = await searchParams;
  const storyKey = jiraKey.toUpperCase();
  const slots: StoryDetailSlots = {
    [StoryDetailTab.TEST_CASES]: <StoryTestCases jiraKey={storyKey} />,
    [StoryDetailTab.GAPS]: <StoryGaps jiraKey={storyKey} />,
    [StoryDetailTab.RUNS]: (
      <StoryRuns jiraKey={storyKey} actions={<NewManualRunButtonLink storyKey={storyKey} />} />
    ),
    [StoryDetailTab.TRACEABILITY]: <StoryTraceability jiraKey={storyKey} />,
  };

  return (
    <StoryDetailPage jiraKey={jiraKey} initialTab={parseStoryDetailTab(tab, slots)} slots={slots} />
  );
};

export default StoryRoute;
