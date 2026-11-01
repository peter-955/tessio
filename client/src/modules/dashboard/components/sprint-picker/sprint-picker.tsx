"use client";

import { DSSelect, type DSSelectOption } from "@/components/design-system";
import { useGetSprints } from "@/modules/sprints/hooks/queries/use-get-sprints";
import type { FC } from "react";
import { useTranslation } from "react-i18next";

interface Props {
  projectKey: string;
  value: string | null;
  onChange: (sprintId: string | null) => void;
}

export const SprintPicker: FC<Props> = ({ projectKey, value, onChange }) => {
  const { t } = useTranslation("dashboard");
  const { data, isError } = useGetSprints(projectKey);

  if (isError || data === undefined || data.length === 0) {
    return null;
  }

  const options: DSSelectOption<string>[] = data.map((sprint) => {
    return {
      value: sprint.id,
      label: t("sprint.option", { name: sprint.name, state: t(`sprint.states.${sprint.state}`) }),
    };
  });

  return (
    <DSSelect
      label={t("sprint.pickerLabel")}
      placeholder={t("sprint.pickerPlaceholder")}
      value={value}
      options={options}
      onChange={onChange}
      isClearable
    />
  );
};
