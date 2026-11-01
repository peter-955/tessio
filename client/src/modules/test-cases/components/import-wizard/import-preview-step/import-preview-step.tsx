"use client";

import {
  DSAlert,
  DSBadge,
  DSButton,
  DSCheckbox,
  DSGroup,
  DSStack,
  DSTable,
  DSText,
} from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { CaseImportRow } from "../../../typing/types/case-import-row.type";
import type { CaseImportPreview } from "../../../typing/types/test-case.type";
import { includeAllCaseImportRows, toggleCaseImportRow } from "../../../utils/import-rows.util";
import { TestCasePriorityBadge } from "../../test-case-priority-badge/test-case-priority-badge";
import { ImportSkippedList } from "../import-skipped-list/import-skipped-list";
import styles from "./import-preview-step.module.scss";

interface Props {
  preview: CaseImportPreview;
  rows: CaseImportRow[];
  isBusy: boolean;
  errorMessage: string | null;
  onRowsChange: (rows: CaseImportRow[]) => void;
  onBack: () => void;
}

const LIST_SEPARATOR = ", ";

export const ImportPreviewStep: FC<Props> = ({
  preview,
  rows,
  isBusy,
  errorMessage,
  onRowsChange,
  onBack,
}) => {
  const { t } = useTranslation("testCases");
  const selectableRows = rows.filter((row) => row.isSelectable);
  const includedCount = rows.filter((row) => row.isIncluded).length;
  const isEverythingIncluded =
    selectableRows.length > 0 && selectableRows.every((row) => row.isIncluded);

  return (
    <DSStack gap={4}>
      <DSGroup justify="between" isWrapping>
        <DSText color="muted">
          {t("import.format", { format: preview.format.toUpperCase() })}
        </DSText>
        <DSButton type="ghost" size="sm" isDisabled={isBusy} onClick={onBack}>
          {t("actions.back")}
        </DSButton>
      </DSGroup>
      {rows.length === 0 ? (
        <DSText color="muted">{t("import.noItems")}</DSText>
      ) : (
        <>
          <DSCheckbox
            label={t("import.selectAll")}
            isChecked={isEverythingIncluded}
            isIndeterminate={includedCount > 0 && !isEverythingIncluded}
            isDisabled={isBusy || selectableRows.length === 0}
            onChange={(isChecked) => {
              onRowsChange(includeAllCaseImportRows(rows, isChecked));
            }}
          />
          <DSTable label={t("import.previewCaption")}>
            <caption className={styles.visuallyHidden}>{t("import.previewCaption")}</caption>
            <thead>
              <tr>
                <th scope="col">{t("import.include")}</th>
                <th scope="col">{t("import.location")}</th>
                <th scope="col">{t("import.story")}</th>
                <th scope="col">{t("import.caseTitle")}</th>
                <th scope="col">{t("import.priority")}</th>
                <th scope="col" className={styles.numeric}>
                  {t("import.steps")}
                </th>
                <th scope="col">{t("import.criteria")}</th>
                <th scope="col">{t("import.notes")}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const { item } = row;
                const unknownCodes = new Set(item.unknownCriterionCodes);
                const knownCodes = item.criterionCodes.filter((code) => !unknownCodes.has(code));

                return (
                  <tr key={item.index}>
                    <td>
                      <DSCheckbox
                        label={
                          <span className={styles.visuallyHidden}>
                            {t("import.includeItem", { title: item.title })}
                          </span>
                        }
                        isChecked={row.isIncluded}
                        isDisabled={!row.isSelectable || isBusy}
                        onChange={(isChecked) => {
                          onRowsChange(toggleCaseImportRow(rows, item.index, isChecked));
                        }}
                      />
                    </td>
                    <td className={styles.location}>{item.location}</td>
                    <td className={styles.code}>{item.storyKey}</td>
                    <td className={styles.title}>{item.title}</td>
                    <td>
                      <TestCasePriorityBadge priority={item.priority} />
                    </td>
                    <td className={styles.numeric}>{item.stepCount}</td>
                    <td>
                      <span className={styles.badges}>
                        {knownCodes.length > 0 && (
                          <span className={styles.code}>{knownCodes.join(LIST_SEPARATOR)}</span>
                        )}
                        {item.unknownCriterionCodes.length > 0 && (
                          <DSBadge color="yellow">
                            {t("import.unknownCriteria", {
                              codes: item.unknownCriterionCodes.join(LIST_SEPARATOR),
                            })}
                          </DSBadge>
                        )}
                      </span>
                    </td>
                    <td>
                      <span className={styles.badges}>
                        {item.isDuplicate && (
                          <DSBadge color="yellow">{t("import.duplicate")}</DSBadge>
                        )}
                        {item.problem !== null && (
                          <DSBadge color="red">{t(`import.problems.${item.problem}`)}</DSBadge>
                        )}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </DSTable>
          {includedCount === 0 && (
            <DSText size="sm" color="muted">
              {t("import.nothingSelected")}
            </DSText>
          )}
        </>
      )}
      <ImportSkippedList skipped={preview.skipped} />
      {errorMessage !== null && <DSAlert color="danger">{errorMessage}</DSAlert>}
    </DSStack>
  );
};
