"use client";

import { DSMultiSelect, type DSSelectOption } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useGetStory } from "@/modules/stories/hooks/queries/use-get-story";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { MAX_CRITERION_LINKS } from "../../../typing/constants/test-case.constant";
import type { LinkedCriterion } from "../../../typing/types/test-case.type";
import { mergeCriterionOptionSources } from "../../../utils/criterion-options.util";

interface Props {
  storyKey: string;
  linkedCriteria: readonly LinkedCriterion[];
  value: string[];
  onChange: (criterionIds: string[]) => void;
  error?: string;
  isDisabled: boolean;
}

export const StoryCriteriaField: FC<Props> = ({
  storyKey,
  linkedCriteria,
  value,
  onChange,
  error,
  isDisabled,
}) => {
  const { t } = useTranslation("testCases");
  const project = useCurrentProject();
  const { data: story } = useGetStory(project.key, storyKey);
  const options = mergeCriterionOptionSources(story?.criteria ?? [], linkedCriteria, value).map(
    (criterion): DSSelectOption<string> => {
      return {
        value: criterion.id,
        label: criterion.isRemoved
          ? t("form.removedCriterion", { code: criterion.code })
          : `${criterion.code} · ${criterion.text}`,
      };
    },
  );

  return (
    <DSMultiSelect<string>
      label={t("form.criteria")}
      placeholder={t("form.criteriaPlaceholder")}
      value={value}
      options={options}
      onChange={onChange}
      error={error}
      maxValues={MAX_CRITERION_LINKS}
      isDisabled={isDisabled}
    />
  );
};
