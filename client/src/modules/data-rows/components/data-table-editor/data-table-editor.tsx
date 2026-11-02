"use client";

import { DSActionIcon, DSButton, DSInput, DSTable, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import {
  DATA_REFERENCE_EXAMPLE,
  MAX_DATA_ROWS,
  MAX_DATA_VALUE_LENGTH,
  MAX_PARAMETER_NAME_LENGTH,
  MAX_PARAMETERS,
  PARAMETER_REFERENCE_PREFIX,
} from "../../typing/constants/data-table.constant";
import type {
  DataTableCellErrorKey,
  DataTableErrors,
} from "../../typing/types/data-table-errors.type";
import type { DataTableValues } from "../../typing/types/data-table.type";
import {
  addDataParameter,
  addDataRow,
  buildCellKey,
  changeDataValue,
  removeDataParameter,
  removeDataRow,
  renameDataParameter,
} from "../../utils/data-table.util";
import styles from "./data-table-editor.module.scss";

interface Props {
  value: DataTableValues;
  onChange: (value: DataTableValues) => void;
  errors: DataTableErrors | null;
  isDisabled: boolean;
}

export const DataTableEditor: FC<Props> = ({ value, onChange, errors, isDisabled }) => {
  const { t } = useTranslation("dataRows");
  const hasParameters = value.parameters.length > 0;

  const translateCellError = (errorKey: DataTableCellErrorKey | undefined): string | undefined => {
    if (errorKey === undefined) {
      return undefined;
    }

    return t(`editor.errors.${errorKey}`, {
      max: errorKey === "tooLong" ? MAX_DATA_VALUE_LENGTH : MAX_PARAMETER_NAME_LENGTH,
    });
  };

  const readParameterLabel = (name: string, position: number): string => {
    return name.trim() === "" ? t("editor.parameterFallback", { position }) : name.trim();
  };

  return (
    <div className={styles.editor}>
      <DSText size="sm" color="muted">
        {t("editor.hint", {
          prefix: PARAMETER_REFERENCE_PREFIX,
          dataExample: DATA_REFERENCE_EXAMPLE,
        })}
      </DSText>
      {errors?.table !== undefined && (
        <DSText size="sm" color="danger">
          {t(`editor.errors.${errors.table}`, {
            max: errors.table === "tooManyRows" ? MAX_DATA_ROWS : MAX_PARAMETERS,
          })}
        </DSText>
      )}
      {hasParameters ? (
        <DSTable label={t("editor.tableLabel")}>
          <caption className={styles.hidden}>{t("editor.tableLabel")}</caption>
          <thead>
            <tr>
              <th scope="col" className={styles.rowHeader}>
                {t("editor.row")}
              </th>
              {value.parameters.map((parameter, index) => {
                const position = index + 1;

                return (
                  <th key={parameter.id} scope="col" className={styles.parameter}>
                    <div className={styles.parameterField}>
                      <DSInput
                        label={t("editor.parameterName", { position })}
                        value={parameter.name}
                        onChange={(name) => {
                          onChange(
                            renameDataParameter(
                              value,
                              parameter.id,
                              name.slice(0, MAX_PARAMETER_NAME_LENGTH),
                            ),
                          );
                        }}
                        placeholder={t("editor.parameterPlaceholder")}
                        error={translateCellError(errors?.parameters[parameter.id])}
                        autoComplete="off"
                        isDisabled={isDisabled}
                        isLabelHidden
                      />
                      {!isDisabled && (
                        <DSActionIcon
                          icon="trash"
                          type="ghost"
                          ariaLabel={t("editor.removeParameter", {
                            name: readParameterLabel(parameter.name, position),
                          })}
                          onClick={() => {
                            onChange(removeDataParameter(value, parameter.id));
                          }}
                        />
                      )}
                    </div>
                  </th>
                );
              })}
              {!isDisabled && (
                <th scope="col">
                  <span className={styles.hidden}>{t("editor.rowActions")}</span>
                </th>
              )}
            </tr>
          </thead>
          <tbody>
            {value.rows.length === 0 && (
              <tr>
                <td colSpan={value.parameters.length + (isDisabled ? 1 : 2)}>
                  <DSText size="sm" color="muted">
                    {t("editor.noRows")}
                  </DSText>
                </td>
              </tr>
            )}
            {value.rows.map((row, rowIndex) => {
              const rowNumber = rowIndex + 1;

              return (
                <tr key={row.id}>
                  <th scope="row" className={styles.rowHeader}>
                    {rowNumber}
                  </th>
                  {value.parameters.map((parameter, parameterIndex) => {
                    return (
                      <td key={parameter.id} className={styles.cell}>
                        <DSInput
                          label={t("editor.cellLabel", {
                            row: rowNumber,
                            parameter: readParameterLabel(parameter.name, parameterIndex + 1),
                          })}
                          value={row.values[parameter.id] ?? ""}
                          onChange={(cellValue) => {
                            onChange(changeDataValue(value, row.id, parameter.id, cellValue));
                          }}
                          error={translateCellError(
                            errors?.values[buildCellKey(row.id, parameter.id)],
                          )}
                          autoComplete="off"
                          isDisabled={isDisabled}
                          isLabelHidden
                        />
                      </td>
                    );
                  })}
                  {!isDisabled && (
                    <td className={styles.rowActions}>
                      <DSActionIcon
                        icon="trash"
                        type="ghost"
                        ariaLabel={t("editor.removeRow", { row: rowNumber })}
                        onClick={() => {
                          onChange(removeDataRow(value, row.id));
                        }}
                      />
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </DSTable>
      ) : (
        <DSText size="sm" color="muted">
          {t("editor.noParameters")}
        </DSText>
      )}
      {!isDisabled && (
        <div className={styles.footer}>
          <DSButton
            type="default"
            icon="plus"
            isDisabled={value.parameters.length >= MAX_PARAMETERS}
            onClick={() => {
              onChange(addDataParameter(value));
            }}
          >
            {t("editor.addParameter")}
          </DSButton>
          <DSButton
            type="default"
            icon="table"
            isDisabled={!hasParameters || value.rows.length >= MAX_DATA_ROWS}
            onClick={() => {
              onChange(addDataRow(value));
            }}
          >
            {t("editor.addRow")}
          </DSButton>
        </div>
      )}
    </div>
  );
};
