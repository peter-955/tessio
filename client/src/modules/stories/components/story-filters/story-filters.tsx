"use client";

import { DSGroup, DSInput, DSSelect, type DSSelectOption } from "@/components/design-system";
import type { Sprint } from "@/modules/sprints/typing/types/sprint.type";
import { useEffect, useEffectEvent, useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { useDebouncedValue } from "../../hooks/use-debounced-value";
import {
  SEARCH_DEBOUNCE_MILLISECONDS,
  STORY_QUERY_MAX_LENGTH,
  TEST_STATUSES,
} from "../../typing/constants/story.constant";
import type { TestStatusFilter } from "../../typing/types/story-filter-option.type";
import type { StoryFilters as StoryFilterValues } from "../../typing/types/story-filters.type";
import styles from "./story-filters.module.scss";

const ALL_OPTION = "all";

interface Props {
  filters: StoryFilterValues;
  onChange: (filters: StoryFilterValues) => void;
  isSprintFilterShown: boolean;
  sprints: Sprint[];
}

export const StoryFilters: FC<Props> = ({ filters, onChange, isSprintFilterShown, sprints }) => {
  const { t } = useTranslation("stories");
  const { t: translateSprints } = useTranslation("sprints");
  const [searchText, setSearchText] = useState(filters.query);
  const [syncedQuery, setSyncedQuery] = useState(filters.query);
  const debouncedSearchText = useDebouncedValue(searchText, SEARCH_DEBOUNCE_MILLISECONDS);

  if (filters.query !== syncedQuery) {
    setSyncedQuery(filters.query);
    if (filters.query !== debouncedSearchText) {
      setSearchText(filters.query);
    }
  }

  const commitSearchText = useEffectEvent((query: string): void => {
    if (query !== filters.query) {
      onChange({ ...filters, query });
    }
  });

  useEffect(() => {
    commitSearchText(debouncedSearchText);
  }, [debouncedSearchText]);

  const sprintOptions: DSSelectOption<string>[] = [
    { value: ALL_OPTION, label: t("filters.allSprints") },
    ...sprints.map((sprint): DSSelectOption<string> => {
      return {
        value: sprint.id,
        label: `${sprint.name} · ${translateSprints(`states.${sprint.state}`)}`,
      };
    }),
  ];
  const statusOptions: DSSelectOption<TestStatusFilter>[] = [
    { value: ALL_OPTION, label: t("filters.allStatuses") },
    ...TEST_STATUSES.map((status): DSSelectOption<TestStatusFilter> => {
      return { value: status, label: t(`testStatuses.${status}`) };
    }),
  ];

  const handleQueryChange = (value: string): void => {
    setSearchText(value.slice(0, STORY_QUERY_MAX_LENGTH));
  };

  const handleSprintChange = (value: string | null): void => {
    onChange({ ...filters, sprintId: value === null || value === ALL_OPTION ? null : value });
  };

  const handleStatusChange = (value: TestStatusFilter | null): void => {
    onChange({ ...filters, testStatus: value === null || value === ALL_OPTION ? null : value });
  };

  return (
    <DSGroup gap={3} align="end" className={styles.filters}>
      <div className={styles.search}>
        <DSInput label={t("filters.search")} value={searchText} onChange={handleQueryChange} />
      </div>
      {isSprintFilterShown && (
        <div className={styles.select}>
          <DSSelect<string>
            label={t("filters.sprint")}
            value={filters.sprintId ?? ALL_OPTION}
            options={sprintOptions}
            onChange={handleSprintChange}
          />
        </div>
      )}
      <div className={styles.select}>
        <DSSelect<TestStatusFilter>
          label={t("filters.status")}
          value={filters.testStatus ?? ALL_OPTION}
          options={statusOptions}
          onChange={handleStatusChange}
        />
      </div>
    </DSGroup>
  );
};
