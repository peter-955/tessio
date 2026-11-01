"use client";

import {
  DSButtonLink,
  DSCard,
  DSEmptyState,
  DSErrorState,
  DSSkeleton,
  DSTabPanel,
  DSTabs,
  type DSTabItem,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { AdfDocument } from "./components/adf-document/adf-document";
import { CriteriaList } from "./components/criteria-list/criteria-list";
import { StoryHeader } from "./components/story-header/story-header";
import { useGetStory } from "./hooks/queries/use-get-story";
import styles from "./story-detail.module.scss";
import {
  NOT_FOUND_STATUS,
  STORY_DETAIL_TAB_PARAMETER,
  STORY_SLOT_TAB_ICONS,
  STORY_SLOT_TAB_LABELS,
  STORY_SLOT_TAB_ORDER,
} from "./typing/constants/story.constant";
import { StoryDetailTab } from "./typing/enums/story-detail-tab.enum";
import type { StoryDetailSlots } from "./typing/types/story-detail-slots.type";
import { parseStoryDetailTab } from "./utils/story-detail-tab.util";
import { buildStoriesPath } from "./utils/story-path.util";

interface Props {
  jiraKey: string;
  initialTab: StoryDetailTab;
  slots: StoryDetailSlots;
}

export const StoryDetailPage: FC<Props> = ({ jiraKey, initialTab, slots }) => {
  const { t } = useTranslation("stories");
  const router = useRouter();
  const project = useCurrentProject();
  const searchParams = useSearchParams();
  const urlTab = parseStoryDetailTab(
    searchParams.get(STORY_DETAIL_TAB_PARAMETER) ?? undefined,
    slots,
  );
  const [activeTab, setActiveTab] = useState(initialTab);
  const [syncedTab, setSyncedTab] = useState(urlTab);
  const { data, error, isPending, isError, isFetching, refetch } = useGetStory(
    project.key,
    jiraKey.toUpperCase(),
  );
  const slotTabs = STORY_SLOT_TAB_ORDER.filter((tab) => {
    return slots[tab] !== undefined;
  });

  if (urlTab !== syncedTab) {
    setSyncedTab(urlTab);
    setActiveTab(urlTab);
  }

  if (isPending) {
    return (
      <div aria-busy="true">
        <DSSkeleton lineCount={8} />
      </div>
    );
  }

  if (error?.status === NOT_FOUND_STATUS) {
    return (
      <DSEmptyState
        title={t("detail.notFound.title")}
        description={t("detail.notFound.description")}
        icon="stories"
        action={
          <DSButtonLink href={buildStoriesPath(project.key)} type="default">
            {t("detail.back")}
          </DSButtonLink>
        }
      />
    );
  }

  if (isError || data === undefined) {
    return (
      <DSErrorState
        title={t("detail.loadError")}
        retryLabel={t("retry")}
        isRetrying={isFetching}
        onRetry={() => {
          void refetch();
        }}
      />
    );
  }

  const tabItems: DSTabItem<StoryDetailTab>[] = [
    { value: StoryDetailTab.OVERVIEW, label: t("tabs.overview"), icon: "file" },
    ...slotTabs.map((tab): DSTabItem<StoryDetailTab> => {
      return {
        value: tab,
        label: t(`tabs.${STORY_SLOT_TAB_LABELS[tab]}`),
        icon: STORY_SLOT_TAB_ICONS[tab],
      };
    }),
  ];

  const handleTabChange = (tab: StoryDetailTab): void => {
    setActiveTab(tab);
    router.replace(`?${STORY_DETAIL_TAB_PARAMETER}=${tab}`, { scroll: false });
  };

  return (
    <>
      <StoryHeader projectKey={project.key} story={data} />
      <DSTabs
        items={tabItems}
        value={activeTab}
        onChange={handleTabChange}
        ariaLabel={t("tabs.ariaLabel")}
      >
        <DSTabPanel value={StoryDetailTab.OVERVIEW}>
          <div className={styles.overview}>
            <DSCard title={t("description.title")}>
              <AdfDocument value={data.description} />
            </DSCard>
            <DSCard title={t("criteria.title")}>
              <CriteriaList criteria={data.criteria} />
            </DSCard>
          </div>
        </DSTabPanel>
        {slotTabs.map((tab) => {
          return (
            <DSTabPanel key={tab} value={tab}>
              {slots[tab]}
            </DSTabPanel>
          );
        })}
      </DSTabs>
    </>
  );
};
