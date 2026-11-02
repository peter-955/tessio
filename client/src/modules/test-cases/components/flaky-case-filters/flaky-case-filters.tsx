"use client";

import { DSCheckbox } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { TestCaseFilters } from "../../typing/types/test-case-filters.type";
import styles from "./flaky-case-filters.module.scss";

interface Props {
  filters: TestCaseFilters;
  onChange: (filters: TestCaseFilters) => void;
}

export const FlakyCaseFilters: FC<Props> = ({ filters, onChange }) => {
  const { t } = useTranslation("flakyCases");

  return (
    <>
      <div className={styles.checkbox}>
        <DSCheckbox
          label={t("filters.flaky")}
          isChecked={filters.isFlaky}
          onChange={(isFlaky) => {
            onChange({ ...filters, isFlaky });
          }}
        />
      </div>
      <div className={styles.checkbox}>
        <DSCheckbox
          label={t("filters.disagreeing")}
          isChecked={filters.isDisagreeing}
          onChange={(isDisagreeing) => {
            onChange({ ...filters, isDisagreeing });
          }}
        />
      </div>
      <div className={styles.checkbox}>
        <DSCheckbox
          label={t("filters.quarantined")}
          isChecked={filters.isQuarantined}
          onChange={(isQuarantined) => {
            onChange({ ...filters, isQuarantined });
          }}
        />
      </div>
    </>
  );
};
