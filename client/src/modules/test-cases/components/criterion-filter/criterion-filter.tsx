"use client";

import { DSSelect } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { ALL_OPTION } from "../../typing/constants/test-case.constant";
import { StoryCriterionFilter } from "./story-criterion-filter/story-criterion-filter";

interface Props {
  storyKey: string | null;
  value: string | null;
  onChange: (criterionId: string | null) => void;
}

export const CriterionFilter: FC<Props> = ({ storyKey, value, onChange }) => {
  const { t } = useTranslation("testCases");

  if (storyKey === null) {
    return (
      <DSSelect<string>
        label={t("filters.criterion")}
        description={t("filters.criterionNeedsStory")}
        value={ALL_OPTION}
        options={[{ value: ALL_OPTION, label: t("filters.allCriteria") }]}
        onChange={() => {
          onChange(null);
        }}
        isDisabled
      />
    );
  }

  return <StoryCriterionFilter storyKey={storyKey} value={value} onChange={onChange} />;
};
