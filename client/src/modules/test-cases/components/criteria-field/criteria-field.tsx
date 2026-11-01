"use client";

import { DSMultiSelect } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { LinkedCriterion } from "../../typing/types/test-case.type";
import { StoryCriteriaField } from "./story-criteria-field/story-criteria-field";

interface Props {
  storyKey: string | null;
  linkedCriteria: readonly LinkedCriterion[];
  value: string[];
  onChange: (criterionIds: string[]) => void;
  error?: string;
  isDisabled: boolean;
}

export const CriteriaField: FC<Props> = ({
  storyKey,
  linkedCriteria,
  value,
  onChange,
  error,
  isDisabled,
}) => {
  const { t } = useTranslation("testCases");

  if (storyKey === null) {
    return (
      <DSMultiSelect<string>
        label={t("form.criteria")}
        description={t("form.criteriaNeedsStory")}
        value={[]}
        options={[]}
        onChange={onChange}
        isDisabled
      />
    );
  }

  return (
    <StoryCriteriaField
      storyKey={storyKey}
      linkedCriteria={linkedCriteria}
      value={value}
      onChange={onChange}
      error={error}
      isDisabled={isDisabled}
    />
  );
};
