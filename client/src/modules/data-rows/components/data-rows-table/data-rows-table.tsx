"use client";

import { DSTable } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { DataRow } from "../../typing/types/data-table.type";
import styles from "./data-rows-table.module.scss";

interface Props {
  parameters: readonly string[];
  dataRows: readonly DataRow[];
}

export const DataRowsTable: FC<Props> = ({ parameters, dataRows }) => {
  const { t } = useTranslation("dataRows");

  return (
    <DSTable label={t("table.label")}>
      <caption className={styles.caption}>{t("table.label")}</caption>
      <thead>
        <tr>
          <th scope="col" className={styles.rowHeader}>
            {t("table.iteration")}
          </th>
          {parameters.map((parameter) => {
            return (
              <th key={parameter} scope="col">
                {parameter}
              </th>
            );
          })}
        </tr>
      </thead>
      <tbody>
        {dataRows.map((row, index) => {
          return (
            <tr key={index}>
              <th scope="row" className={styles.rowHeader}>
                {index + 1}
              </th>
              {parameters.map((parameter) => {
                return (
                  <td key={parameter} className={styles.value}>
                    {row[parameter] ?? ""}
                  </td>
                );
              })}
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
