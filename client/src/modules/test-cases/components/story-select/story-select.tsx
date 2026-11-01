"use client";

import { DSSelect, type DSSelectOption } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useGetStories } from "@/modules/stories/hooks/queries/use-get-stories";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { ALL_OPTION, ALL_STORIES_FILTERS } from "../../typing/constants/test-case.constant";

interface Props {
  label: string;
  value: string | null;
  onChange: (storyKey: string | null) => void;
  allLabel?: string;
  placeholder?: string;
  error?: string;
  isRequired?: boolean;
  isDisabled?: boolean;
}

export const StorySelect: FC<Props> = ({
  label,
  value,
  onChange,
  allLabel,
  placeholder,
  error,
  isRequired = false,
  isDisabled = false,
}) => {
  const { t } = useTranslation("testCases");
  const project = useCurrentProject();
  const { data: stories = [] } = useGetStories(project.key, ALL_STORIES_FILTERS);
  const storyOptions = stories.map((story): DSSelectOption<string> => {
    return { value: story.jiraKey, label: `${story.jiraKey} · ${story.title}` };
  });
  const isValueListed = storyOptions.some((option) => {
    return option.value === value;
  });
  const options: DSSelectOption<string>[] = [
    ...(allLabel === undefined ? [] : [{ value: ALL_OPTION, label: allLabel }]),
    ...(value !== null && !isValueListed ? [{ value, label: value }] : []),
    ...storyOptions,
  ];

  const handleChange = (selectedValue: string | null): void => {
    onChange(selectedValue === null || selectedValue === ALL_OPTION ? null : selectedValue);
  };

  return (
    <DSSelect<string>
      label={label}
      value={value ?? (allLabel === undefined ? null : ALL_OPTION)}
      options={options}
      onChange={handleChange}
      placeholder={placeholder}
      error={error}
      nothingFoundLabel={t("filters.noStories")}
      isRequired={isRequired}
      isDisabled={isDisabled}
      isSearchable
    />
  );
};
