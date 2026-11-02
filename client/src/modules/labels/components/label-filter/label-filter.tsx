"use client";

import { DSMultiSelect } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetLabels } from "../../hooks/queries/use-get-labels";
import { MAX_LABELS_PER_CASE } from "../../typing/constants/label.constant";
import { buildLabelFilterChoices } from "../../utils/label-filter.util";

interface Props {
  value: string[];
  onChange: (labelNames: string[]) => void;
}

export const LabelFilter: FC<Props> = ({ value, onChange }) => {
  const { t } = useTranslation("labels");
  const project = useCurrentProject();
  const { data: labels = [] } = useGetLabels(project.key);

  if (labels.length === 0 && value.length === 0) {
    return null;
  }

  const choices = buildLabelFilterChoices(labels, value);

  return (
    <DSMultiSelect<string>
      label={t("filter.label")}
      value={choices.value}
      options={choices.options}
      onChange={onChange}
      placeholder={value.length === 0 ? t("filter.placeholder") : undefined}
      nothingFoundLabel={t("filter.noMatch")}
      maxValues={MAX_LABELS_PER_CASE}
    />
  );
};
