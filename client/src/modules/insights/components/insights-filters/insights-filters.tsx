"use client";

import {
  DSDateInput,
  DSSegmentedControl,
  DSSelect,
  type DSSegmentedOption,
  type DSSelectOption,
} from "@/components/design-system";
import { useGetSprints } from "@/modules/sprints/hooks/queries/use-get-sprints";
import type { Sprint } from "@/modules/sprints/typing/types/sprint.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { TREND_GROUPINGS } from "../../typing/constants/insights.constant";
import type { InsightsRange } from "../../typing/types/insights-range.type";
import type { TrendGrouping } from "../../typing/types/insights.type";
import styles from "./insights-filters.module.scss";

interface Props {
  projectKey: string;
  range: InsightsRange;
  groupBy: TrendGrouping;
  sprintId: string | null;
  onFromChange: (day: string | null) => void;
  onToChange: (day: string | null) => void;
  onSprintChange: (sprint: Sprint | null) => void;
  onGroupByChange: (groupBy: TrendGrouping) => void;
}

export const InsightsFilters: FC<Props> = ({
  projectKey,
  range,
  groupBy,
  sprintId,
  onFromChange,
  onToChange,
  onSprintChange,
  onGroupByChange,
}) => {
  const { t } = useTranslation("insights");
  const { data: sprints } = useGetSprints(projectKey);
  const datedSprints = (sprints ?? []).filter((sprint) => {
    return sprint.startAt !== null;
  });
  const sprintOptions: DSSelectOption<string>[] = datedSprints.map((sprint) => {
    return {
      value: sprint.id,
      label: t("filters.sprintOption", {
        name: sprint.name,
        state: t(`filters.sprintStates.${sprint.state}`),
      }),
    };
  });
  const groupOptions: DSSegmentedOption<TrendGrouping>[] = TREND_GROUPINGS.map((grouping) => {
    return { value: grouping, label: t(`filters.groupBy.${grouping}`) };
  });

  const handleSprintChange = (value: string | null): void => {
    const sprint =
      datedSprints.find((candidate) => {
        return candidate.id === value;
      }) ?? null;
    onSprintChange(sprint);
  };

  return (
    <div className={styles.filters}>
      <div className={styles.field}>
        <DSDateInput
          label={t("filters.from")}
          value={range.from}
          onChange={onFromChange}
          isClearable={false}
        />
      </div>
      <div className={styles.field}>
        <DSDateInput
          label={t("filters.to")}
          value={range.to}
          onChange={onToChange}
          isClearable={false}
        />
      </div>
      {sprintOptions.length > 0 && (
        <div className={styles.sprint}>
          <DSSelect
            label={t("filters.sprint")}
            placeholder={t("filters.sprintPlaceholder")}
            value={sprintId}
            options={sprintOptions}
            onChange={handleSprintChange}
            isClearable
          />
        </div>
      )}
      <div className={styles.grouping}>
        <span className={styles.groupingLabel} aria-hidden="true">
          {t("filters.groupByLabel")}
        </span>
        <DSSegmentedControl
          value={groupBy}
          options={groupOptions}
          onChange={onGroupByChange}
          ariaLabel={t("filters.groupByLabel")}
        />
      </div>
    </div>
  );
};
