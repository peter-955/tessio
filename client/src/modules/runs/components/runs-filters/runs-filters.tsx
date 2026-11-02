"use client";

import {
  DSSegmentedControl,
  DSSelect,
  type DSSegmentedOption,
  type DSSelectOption,
} from "@/components/design-system";
import { SuiteSelect } from "@/modules/suites/components/suite-select/suite-select";
import { RUN_STATUSES } from "@/shared/typing/constants/test-status.constant";
import type { RunStatus } from "@/shared/typing/types/test-run.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetRunStoryOptions } from "../../hooks/queries/use-get-run-story-options";
import { ALL_OPTION } from "../../typing/constants/run.constant";
import type { RunFilters } from "../../typing/types/run.type";
import styles from "./runs-filters.module.scss";

type StatusOption = RunStatus | typeof ALL_OPTION;

interface Props {
  projectKey: string;
  filters: RunFilters;
  onChange: (filters: RunFilters) => void;
}

export const RunsFilters: FC<Props> = ({ projectKey, filters, onChange }) => {
  const { t } = useTranslation("runs");
  const { t: tSuites } = useTranslation("suites");
  const { data: storyOptions = [] } = useGetRunStoryOptions(projectKey);
  const isStoryListed = storyOptions.some((option) => {
    return option.value === filters.storyKey;
  });
  const options: DSSelectOption<string>[] =
    filters.storyKey !== null && !isStoryListed
      ? [{ value: filters.storyKey, label: filters.storyKey }, ...storyOptions]
      : storyOptions;
  const statusOptions: DSSegmentedOption<StatusOption>[] = [
    { value: ALL_OPTION, label: t("filters.all") },
    ...RUN_STATUSES.map((status): DSSegmentedOption<StatusOption> => {
      return { value: status, label: t(`status.${status}`) };
    }),
  ];

  const handleStatusChange = (value: StatusOption): void => {
    onChange({ ...filters, status: value === ALL_OPTION ? null : value });
  };

  const handleStoryChange = (storyKey: string | null): void => {
    onChange({ ...filters, storyKey, suiteId: storyKey === null ? filters.suiteId : null });
  };

  const handleSuiteChange = (suiteId: string | null): void => {
    onChange({ ...filters, suiteId, storyKey: suiteId === null ? filters.storyKey : null });
  };

  return (
    <div className={styles.filters}>
      <div className={styles.status}>
        <DSSegmentedControl<StatusOption>
          value={filters.status ?? ALL_OPTION}
          options={statusOptions}
          onChange={handleStatusChange}
          ariaLabel={t("filters.statusLabel")}
        />
      </div>
      <div className={styles.story}>
        <DSSelect<string>
          label={t("filters.storyLabel")}
          placeholder={t("filters.storyPlaceholder")}
          value={filters.storyKey}
          options={options}
          onChange={handleStoryChange}
          isSearchable
          isClearable
        />
      </div>
      <SuiteSelect
        className={styles.story}
        projectKey={projectKey}
        value={filters.suiteId}
        onChange={handleSuiteChange}
        label={tSuites("runs.filterLabel")}
        placeholder={tSuites("runs.filterPlaceholder")}
        isArchivedIncluded
        isHiddenWithoutSuites
        isClearable
      />
    </div>
  );
};
