"use client";

import { DSCard } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { MissingScreenshot } from "../../../typing/types/run.type";
import styles from "./report-missing-screenshots.module.scss";

interface Props {
  missingScreenshots: MissingScreenshot[];
}

export const ReportMissingScreenshots: FC<Props> = ({ missingScreenshots }) => {
  const { t } = useTranslation("runs");

  if (missingScreenshots.length === 0) {
    return null;
  }

  return (
    <DSCard title={t("report.missingScreenshots")}>
      <ul className={styles.list}>
        {missingScreenshots.map((screenshot) => {
          return (
            <li key={`${screenshot.caseResultId}-${String(screenshot.stepOrder)}`}>
              {t("report.missingItem", { code: screenshot.code, order: screenshot.stepOrder })}
            </li>
          );
        })}
      </ul>
    </DSCard>
  );
};
