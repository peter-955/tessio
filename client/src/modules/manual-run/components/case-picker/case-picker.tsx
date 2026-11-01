"use client";

import { DSButton, DSCheckbox, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { ReadyTestCase } from "../../typing/types/manual-run.type";
import styles from "./case-picker.module.scss";

interface Props {
  cases: ReadyTestCase[];
  selectedIds: readonly string[];
  onChange: (selectedIds: string[]) => void;
  isDisabled?: boolean;
}

export const CasePicker: FC<Props> = ({ cases, selectedIds, onChange, isDisabled = false }) => {
  const { t } = useTranslation("manualRun");
  const isAllSelected = cases.length > 0 && selectedIds.length === cases.length;

  const handleToggleAll = (): void => {
    onChange(
      isAllSelected
        ? []
        : cases.map((testCase) => {
            return testCase.id;
          }),
    );
  };

  const handleCaseChange = (testCaseId: string, isChecked: boolean): void => {
    onChange(
      cases
        .filter((testCase) => {
          return testCase.id === testCaseId ? isChecked : selectedIds.includes(testCase.id);
        })
        .map((testCase) => {
          return testCase.id;
        }),
    );
  };

  return (
    <fieldset className={styles.picker} disabled={isDisabled}>
      <legend className={styles.legend}>{t("new.cases")}</legend>
      <div className={styles.toolbar}>
        <DSText size="sm" color="muted" component="span">
          {t("new.selectedCount", { selected: selectedIds.length, total: cases.length })}
        </DSText>
        <DSButton type="ghost" size="sm" isDisabled={isDisabled} onClick={handleToggleAll}>
          {isAllSelected ? t("new.clearAll") : t("new.selectAll")}
        </DSButton>
      </div>
      <ul className={styles.list}>
        {cases.map((testCase) => {
          return (
            <li key={testCase.id} className={styles.item}>
              <DSCheckbox
                label={`${testCase.code} · ${testCase.title} · ${t("new.stepCount", { count: testCase.stepCount })}`}
                isChecked={selectedIds.includes(testCase.id)}
                isDisabled={isDisabled}
                onChange={(isChecked) => {
                  handleCaseChange(testCase.id, isChecked);
                }}
              />
            </li>
          );
        })}
      </ul>
    </fieldset>
  );
};
