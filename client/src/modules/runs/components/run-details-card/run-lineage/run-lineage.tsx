"use client";

import { DSText } from "@/components/design-system";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { buildRunPath } from "../../../utils/run-path.util";
import styles from "./run-lineage.module.scss";

interface Props {
  projectKey: string;
  parentRunId: string | null;
  childRunIds: string[];
}

export const RunLineage: FC<Props> = ({ projectKey, parentRunId, childRunIds }) => {
  const { t } = useTranslation("runs");

  if (parentRunId === null && childRunIds.length === 0) {
    return null;
  }

  return (
    <div className={styles.lineage}>
      {parentRunId !== null && (
        <Link href={buildRunPath(projectKey, parentRunId)}>{t("lineage.rerunOf")}</Link>
      )}
      {childRunIds.length > 0 && (
        <div className={styles.children}>
          <DSText size="xs" color="muted" component="span">
            {t("lineage.reruns")}
          </DSText>
          <ul className={styles.list}>
            {childRunIds.map((childRunId, index) => {
              return (
                <li key={childRunId}>
                  <Link href={buildRunPath(projectKey, childRunId)}>
                    {t("lineage.rerunNumber", { number: index + 1 })}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
};
