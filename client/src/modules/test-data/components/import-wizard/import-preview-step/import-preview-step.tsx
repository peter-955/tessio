"use client";

import {
  DSAlert,
  DSBadge,
  DSButton,
  DSCheckbox,
  DSGroup,
  DSSegmentedControl,
  DSStack,
  DSTable,
  DSText,
  type DSSegmentedOption,
} from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { IMPORT_ACTION_BADGE_COLORS } from "../../../typing/constants/import.constant";
import { DATA_ITEM_KINDS, SECRET_MASK } from "../../../typing/constants/test-data.constant";
import type { DataItemKind } from "../../../typing/types/data-item.type";
import type { ImportRow } from "../../../typing/types/import-row.type";
import type { ImportPreview } from "../../../typing/types/import.type";
import { isImportRowLocked } from "../../../utils/import-rows.util";
import { ImportSkippedList } from "../import-skipped-list/import-skipped-list";
import styles from "./import-preview-step.module.scss";

interface Props {
  preview: ImportPreview;
  rows: ImportRow[];
  scopeName: string;
  canEditSecrets: boolean;
  isBusy: boolean;
  errorMessage: string | null;
  onRowsChange: (rows: ImportRow[]) => void;
  onBack: () => void;
}

export const ImportPreviewStep: FC<Props> = ({
  preview,
  rows,
  scopeName,
  canEditSecrets,
  isBusy,
  errorMessage,
  onRowsChange,
  onBack,
}) => {
  const { t } = useTranslation("testData");
  const selectableRows = rows.filter((row) => !isImportRowLocked(row, canEditSecrets));
  const includedCount = rows.filter((row) => row.isIncluded).length;
  const hasLockedRows = selectableRows.length < rows.length;
  const isEverythingIncluded =
    selectableRows.length > 0 && selectableRows.every((row) => row.isIncluded);

  const kindOptions: DSSegmentedOption<DataItemKind>[] = DATA_ITEM_KINDS.filter((kind) => {
    return canEditSecrets || kind !== "secret";
  }).map((kind) => {
    return { value: kind, label: t(`kind.${kind}`) };
  });

  const updateRow = (key: string, update: Partial<ImportRow>): void => {
    onRowsChange(
      rows.map((row) => {
        return row.key === key ? { ...row, ...update } : row;
      }),
    );
  };

  const handleSelectAll = (isChecked: boolean): void => {
    onRowsChange(
      rows.map((row) => {
        return isImportRowLocked(row, canEditSecrets) ? row : { ...row, isIncluded: isChecked };
      }),
    );
  };

  return (
    <DSStack gap={4}>
      <DSGroup justify="between" isWrapping>
        <DSText color="muted">{t("import.previewStepTitle")}</DSText>
        <DSButton type="ghost" size="sm" isDisabled={isBusy} onClick={onBack}>
          {t("actions.back")}
        </DSButton>
      </DSGroup>
      <dl className={styles.summary}>
        <div className={styles.summaryItem}>
          <dt className={styles.summaryLabel}>{t("import.format")}</dt>
          <dd>{t(`import.formatName.${preview.format}`)}</dd>
        </div>
        <div className={styles.summaryItem}>
          <dt className={styles.summaryLabel}>{t("import.scope")}</dt>
          <dd>{scopeName}</dd>
        </div>
      </dl>
      {hasLockedRows && <DSAlert color="info">{t("import.secretLocked")}</DSAlert>}
      {rows.length === 0 ? (
        <DSText color="muted">{t("import.noRows")}</DSText>
      ) : (
        <>
          <DSCheckbox
            label={t("actions.selectAll")}
            isChecked={isEverythingIncluded}
            isIndeterminate={includedCount > 0 && !isEverythingIncluded}
            isDisabled={isBusy || selectableRows.length === 0}
            onChange={handleSelectAll}
          />
          <DSTable label={t("import.previewStepTitle")}>
            <caption className={styles.caption}>{t("import.previewStepTitle")}</caption>
            <thead>
              <tr>
                <th scope="col">{t("import.include")}</th>
                <th scope="col">{t("import.key")}</th>
                <th scope="col">{t("import.value")}</th>
                <th scope="col">{t("import.kind")}</th>
                <th scope="col">{t("import.actionColumn")}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const isLocked = isImportRowLocked(row, canEditSecrets);

                return (
                  <tr key={row.key}>
                    <td>
                      <DSCheckbox
                        label={
                          <span className={styles.visuallyHidden}>
                            {t("import.includeKey", { key: row.key })}
                          </span>
                        }
                        isChecked={row.isIncluded}
                        isDisabled={isLocked || isBusy}
                        onChange={(isChecked) => {
                          updateRow(row.key, { isIncluded: isChecked });
                        }}
                      />
                    </td>
                    <td className={styles.key}>
                      {row.key}
                      {row.description !== null && (
                        <span className={styles.description}>{row.description}</span>
                      )}
                    </td>
                    <td>
                      {row.value === null ? (
                        <span className={styles.mask}>{SECRET_MASK}</span>
                      ) : (
                        <span className={styles.value} title={row.value}>
                          {row.value}
                        </span>
                      )}
                    </td>
                    <td>
                      {isLocked ? (
                        <DSBadge color="yellow">{t(`kind.${row.kind}`)}</DSBadge>
                      ) : (
                        <DSSegmentedControl
                          ariaLabel={t("import.kindOf", { key: row.key })}
                          value={row.kind}
                          options={kindOptions}
                          size="xs"
                          onChange={(kind) => {
                            updateRow(row.key, { kind });
                          }}
                        />
                      )}
                    </td>
                    <td>
                      <DSBadge color={IMPORT_ACTION_BADGE_COLORS[row.action]}>
                        {t(`import.action.${row.action}`)}
                      </DSBadge>
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
