"use client";

import { DSStack, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { CaseImportSkip } from "../../../typing/types/test-case.type";
import styles from "./import-skipped-list.module.scss";

interface Props {
  skipped: readonly CaseImportSkip[];
}

export const ImportSkippedList: FC<Props> = ({ skipped }) => {
  const { t } = useTranslation("testCases");

  if (skipped.length === 0) {
    return null;
  }

  return (
    <DSStack gap={2}>
      <DSText weight="medium">{t("import.skipped")}</DSText>
      <ul className={styles.list}>
        {skipped.map((skip) => {
          return (
            <li key={`${skip.location}-${skip.reason}`}>
              <span className={styles.location}>{skip.location}</span>
              <span className={styles.reason}>{t(`import.skipReasons.${skip.reason}`)}</span>
            </li>
          );
        })}
      </ul>
    </DSStack>
  );
};
