"use client";

import { DSSelect } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetSuites } from "../../hooks/queries/use-get-suites";
import { buildSuiteOptions, type SuiteOptionSource } from "../../utils/suite-options.util";

interface Props {
  projectKey: string;
  value: string | null;
  selectedSuite?: SuiteOptionSource | null;
  onChange: (suiteId: string | null) => void;
  label: string;
  placeholder: string;
  isArchivedIncluded?: boolean;
  isHiddenWithoutSuites?: boolean;
  isClearable?: boolean;
  isRequired?: boolean;
  isDisabled?: boolean;
  className?: string;
}

export const SuiteSelect: FC<Props> = ({
  projectKey,
  value,
  selectedSuite = null,
  onChange,
  label,
  placeholder,
  isArchivedIncluded = false,
  isHiddenWithoutSuites = false,
  isClearable = false,
  isRequired = false,
  isDisabled = false,
  className,
}) => {
  const { t } = useTranslation("suites");
  const { data: suites = [] } = useGetSuites(projectKey, isArchivedIncluded);

  if (isHiddenWithoutSuites && suites.length === 0 && value === null) {
    return null;
  }

  const options = buildSuiteOptions(
    suites,
    value,
    (name) => {
      return t("runs.archivedOption", { name });
    },
    selectedSuite,
  );

  return (
    <div className={className}>
      <DSSelect<string>
        label={label}
        value={value}
        options={options}
        onChange={onChange}
        placeholder={placeholder}
        nothingFoundLabel={t("manualRun.noSuites")}
        isSearchable
        isClearable={isClearable}
        isRequired={isRequired}
        isDisabled={isDisabled}
      />
    </div>
  );
};
