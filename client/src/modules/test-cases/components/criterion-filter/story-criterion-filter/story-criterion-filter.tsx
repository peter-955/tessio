"use client";

import { DSSelect, type DSSelectOption } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useGetStory } from "@/modules/stories/hooks/queries/use-get-story";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { ALL_OPTION } from "../../../typing/constants/test-case.constant";

interface Props {
  storyKey: string;
  value: string | null;
  onChange: (criterionId: string | null) => void;
}

export const StoryCriterionFilter: FC<Props> = ({ storyKey, value, onChange }) => {
  const { t } = useTranslation("testCases");
  const project = useCurrentProject();
  const { data: story } = useGetStory(project.key, storyKey);
  const criteria = story?.criteria ?? [];
  const options: DSSelectOption<string>[] = [
    { value: ALL_OPTION, label: t("filters.allCriteria") },
    ...criteria
      .filter((criterion) => !criterion.isRemoved || criterion.id === value)
      .map((criterion): DSSelectOption<string> => {
        return {
          value: criterion.id,
          label: criterion.isRemoved
            ? t("form.removedCriterion", { code: criterion.code })
            : `${criterion.code} · ${criterion.text}`,
        };
      }),
  ];
  const isValueListed = options.some((option) => option.value === value);

  const handleChange = (selectedValue: string | null): void => {
    onChange(selectedValue === null || selectedValue === ALL_OPTION ? null : selectedValue);
  };

  return (
    <DSSelect<string>
      label={t("filters.criterion")}
      value={value !== null && isValueListed ? value : ALL_OPTION}
      options={options}
      onChange={handleChange}
      isSearchable
    />
  );
};
