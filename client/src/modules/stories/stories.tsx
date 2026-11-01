"use client";

import { DSPageHeader } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useGetSprints } from "@/modules/sprints/hooks/queries/use-get-sprints";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { StoryFilters } from "./components/story-filters/story-filters";
import { StoryList } from "./components/story-list/story-list";
import { SyncControl } from "./components/sync-control/sync-control";
import type { StoryFilters as StoryFilterValues } from "./typing/types/story-filters.type";
import {
  buildStoryFiltersSearch,
  parseStoryFilters,
  readStorySearchParams,
} from "./utils/story-filters.util";

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
        actions={<SyncControl />}
      />
      <StoryFilters
        filters={filters}
        onChange={handleFiltersChange}
        isSprintFilterShown={!sprintsQuery.isError}
        sprints={sprintsQuery.data ?? []}
      />
      <StoryList projectKey={project.key} filters={filters} isSprintColumnShown />
    </>
  );
};
