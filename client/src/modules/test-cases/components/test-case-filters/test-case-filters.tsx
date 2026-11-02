"use client";

import { DSCheckbox, DSInput, DSSelect, type DSSelectOption } from "@/components/design-system";
import { LabelFilter } from "@/modules/labels/components/label-filter/label-filter";
import { useDebouncedValue } from "@/modules/stories/hooks/use-debounced-value";
import { useEffect, useEffectEvent, useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import {
  ALL_OPTION,
  QUERY_MAX_LENGTH,
  SEARCH_DEBOUNCE_MILLISECONDS,
  TEST_CASE_PRIORITIES,
  TEST_CASE_STATUSES,
} from "../../typing/constants/test-case.constant";
import type { TestCaseFilters as TestCaseFilterValues } from "../../typing/types/test-case-filters.type";
import type { TestCasePriority, TestCaseStatus } from "../../typing/types/test-case.type";
import { CriterionFilter } from "../criterion-filter/criterion-filter";
import { FlakyCaseFilters } from "../flaky-case-filters/flaky-case-filters";
import { StorySelect } from "../story-select/story-select";
import styles from "./test-case-filters.module.scss";

type StatusOption = TestCaseStatus | typeof ALL_OPTION;

type PriorityOption = TestCasePriority | typeof ALL_OPTION;

interface Props {
  filters: TestCaseFilterValues;
  onChange: (filters: TestCaseFilterValues) => void;
  isStoryFilterShown: boolean;
}

export const TestCaseFilters: FC<Props> = ({ filters, onChange, isStoryFilterShown }) => {
  const { t } = useTranslation("testCases");
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

  const statusOptions: DSSelectOption<StatusOption>[] = [
    { value: ALL_OPTION, label: t("filters.allStatuses") },
    ...TEST_CASE_STATUSES.map((status): DSSelectOption<StatusOption> => {
      return { value: status, label: t(`status.${status}`) };
    }),
  ];
  const priorityOptions: DSSelectOption<PriorityOption>[] = [
    { value: ALL_OPTION, label: t("filters.allPriorities") },
    ...TEST_CASE_PRIORITIES.map((priority): DSSelectOption<PriorityOption> => {
      return { value: priority, label: t(`priority.${priority}`) };
    }),
  ];

  const handleQueryChange = (value: string): void => {
    setSearchText(value.slice(0, QUERY_MAX_LENGTH));
  };

  const handleStoryChange = (storyKey: string | null): void => {
    onChange({ ...filters, storyKey, criterionId: null });
  };

  const handleStatusChange = (value: StatusOption | null): void => {
    onChange({ ...filters, status: value === null || value === ALL_OPTION ? null : value });
  };

  const handlePriorityChange = (value: PriorityOption | null): void => {
    onChange({ ...filters, priority: value === null || value === ALL_OPTION ? null : value });
  };

  return (
    <div className={styles.filters}>
      <div className={styles.search}>
        <DSInput
          label={t("filters.search")}
          placeholder={t("filters.searchPlaceholder")}
          value={searchText}
          onChange={handleQueryChange}
        />
      </div>
      {isStoryFilterShown && (
        <StorySelect
          label={t("filters.story")}
          value={filters.storyKey}
          onChange={handleStoryChange}
          allLabel={t("filters.allStories")}
        />
      )}
      <CriterionFilter
        storyKey={filters.storyKey}
        value={filters.criterionId}
        onChange={(criterionId) => {
          onChange({ ...filters, criterionId });
        }}
      />
      <DSSelect<StatusOption>
        label={t("filters.status")}
        value={filters.status ?? ALL_OPTION}
        options={statusOptions}
        onChange={handleStatusChange}
      />
      <DSSelect<PriorityOption>
        label={t("filters.priority")}
        value={filters.priority ?? ALL_OPTION}
        options={priorityOptions}
        onChange={handlePriorityChange}
      />
      <LabelFilter
        value={filters.labelNames}
        onChange={(labelNames) => {
          onChange({ ...filters, labelNames });
        }}
      />
      <div className={styles.checkbox}>
        <DSCheckbox
          label={t("filters.needsReview")}
          isChecked={filters.isNeedingReview}
          onChange={(isNeedingReview) => {
            onChange({ ...filters, isNeedingReview });
          }}
        />
      </div>
      <FlakyCaseFilters filters={filters} onChange={onChange} />
    </div>
  );
};
