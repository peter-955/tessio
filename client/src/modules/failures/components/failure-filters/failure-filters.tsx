"use client";

import { DSSelect, type DSSelectOption } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { StorySelect } from "@/modules/test-cases/components/story-select/story-select";
import { useGetProjectMembers } from "@/shared/hooks/queries/use-get-project-members";
import { useMemo, type FC } from "react";
import { useTranslation } from "react-i18next";
import {
  ACTIVE_FILTER,
  ALL_FILTER,
  ANY_ASSIGNEE_OPTION,
  FAILURE_STATUSES,
} from "../../typing/constants/failure.constant";
import type {
  FailureFilters as FailureFilterValues,
  FailureStatusFilter,
} from "../../typing/types/failure-filters.type";
import { buildAssigneeFilterOptions } from "../../utils/assignee-options.util";
import styles from "./failure-filters.module.scss";

interface Props {
  filters: FailureFilterValues;
  onChange: (filters: FailureFilterValues) => void;
}

export const FailureFilters: FC<Props> = ({ filters, onChange }) => {
  const { t } = useTranslation("failures");
  const project = useCurrentProject();
  const members = useGetProjectMembers(project.key);
  const statusOptions: DSSelectOption<FailureStatusFilter>[] = [
    { value: ACTIVE_FILTER, label: t("filters.active") },
    { value: ALL_FILTER, label: t("filters.all") },
    ...FAILURE_STATUSES.map((status): DSSelectOption<FailureStatusFilter> => {
      return { value: status, label: t(`status.${status}`) };
    }),
  ];
  const memberOptions = useMemo(() => {
    return buildAssigneeFilterOptions(members.data ?? [], {
      anyone: t("filters.anyone"),
      unassigned: t("filters.unassigned"),
      me: t("filters.me"),
      formatDeactivated: (name) => {
        return t("filters.deactivatedMember", { name });
      },
    });
  }, [members.data, t]);
  const isAssigneeListed = memberOptions.some((option) => {
    return option.value === filters.assignee;
  });
  const assigneeOptions: DSSelectOption<string>[] =
    filters.assignee === null || isAssigneeListed
      ? memberOptions
      : [...memberOptions, { value: filters.assignee, label: filters.assignee }];

  const handleStatusChange = (status: FailureStatusFilter | null): void => {
    onChange({ ...filters, status: status ?? ACTIVE_FILTER });
  };

  const handleAssigneeChange = (value: string | null): void => {
    onChange({
      ...filters,
      assignee: value === null || value === ANY_ASSIGNEE_OPTION ? null : value,
    });
  };

  const handleStoryChange = (storyKey: string | null): void => {
    onChange({ ...filters, storyKey });
  };

  return (
    <div className={styles.filters}>
      <DSSelect<FailureStatusFilter>
        label={t("filters.status")}
        value={filters.status}
        options={statusOptions}
        onChange={handleStatusChange}
      />
      <DSSelect<string>
        label={t("filters.assignee")}
        value={filters.assignee ?? ANY_ASSIGNEE_OPTION}
        options={assigneeOptions}
        onChange={handleAssigneeChange}
        isSearchable
      />
      <StorySelect
        label={t("filters.story")}
        value={filters.storyKey}
        onChange={handleStoryChange}
        allLabel={t("filters.allStories")}
      />
    </div>
  );
};
