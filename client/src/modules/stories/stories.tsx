"use client";

import { DSButton, DSPageHeader } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import { useGetSprints } from "@/modules/sprints/hooks/queries/use-get-sprints";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { StoryEditorModal } from "./components/story-editor-modal/story-editor-modal";
import { StoryFilters } from "./components/story-filters/story-filters";
import { StoryList } from "./components/story-list/story-list";
import { SyncControl } from "./components/sync-control/sync-control";
import type { StoryFilters as StoryFilterValues } from "./typing/types/story-filters.type";
import {
  buildStoryFiltersSearch,
  parseStoryFilters,
  readStorySearchParams,
} from "./utils/story-filters.util";
import { buildStoryPath } from "./utils/story-path.util";

interface Props {
  initialFilters: StoryFilterValues;
}

export const StoriesPage: FC<Props> = ({ initialFilters }) => {
  const { t } = useTranslation("stories");
  const router = useRouter();
  const pathname = usePathname();
  const project = useCurrentProject();
  const searchParams = useSearchParams();
  const search = searchParams.toString();
  const [filters, setFilters] = useState<StoryFilterValues>(initialFilters);
  const [syncedSearch, setSyncedSearch] = useState(search);
  const sprintsQuery = useGetSprints(project.key);
  const [isEditorOpened, setIsEditorOpened] = useState(false);
  const canWriteStories =
    !project.isLinkedToJira && checkHasProjectCapability(project, "story.edit");

  if (search !== syncedSearch) {
    setSyncedSearch(search);
    const urlFilters = parseStoryFilters(readStorySearchParams(searchParams));
    if (buildStoryFiltersSearch(urlFilters) !== buildStoryFiltersSearch(filters)) {
      setFilters(urlFilters);
    }
  }

  const handleFiltersChange = (nextFilters: StoryFilterValues): void => {
    setFilters(nextFilters);
    router.replace(`${pathname}${buildStoryFiltersSearch(nextFilters)}`, { scroll: false });
  };

  return (
    <>
      <DSPageHeader
        title={t("title")}
        description={t("pageDescription")}
        actions={
          project.isLinkedToJira ? (
            <SyncControl />
          ) : (
            canWriteStories && (
              <DSButton
                type="primary"
                icon="plus"
                onClick={() => {
                  setIsEditorOpened(true);
                }}
              >
                {t("editor.newStory")}
              </DSButton>
            )
          )
        }
      />
      <StoryFilters
        filters={filters}
        onChange={handleFiltersChange}
        isSprintFilterShown={project.isLinkedToJira && !sprintsQuery.isError}
        sprints={sprintsQuery.data ?? []}
      />
      <StoryList
        projectKey={project.key}
        filters={filters}
        isSprintColumnShown={project.isLinkedToJira}
      />
      {isEditorOpened && (
        <StoryEditorModal
          projectKey={project.key}
          story={null}
          onClose={() => {
            setIsEditorOpened(false);
          }}
          onSaved={(story) => {
            router.push(buildStoryPath(project.key, story.jiraKey));
          }}
        />
      )}
    </>
  );
};
