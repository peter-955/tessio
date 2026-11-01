"use client";

import type { RunDetail } from "@/shared/typing/types/test-run.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { RunCaseCard } from "./run-case-card/run-case-card";
import styles from "./run-case-list.module.scss";

interface Props {
  projectKey: string;
  run: RunDetail;
}

export const RunCaseList: FC<Props> = ({ projectKey, run }) => {
  const { t } = useTranslation("runs");

  return (
    <ul className={styles.list} aria-label={t("case.listLabel")}>
      {run.cases.map((runCase) => {
        return (
          <RunCaseCard
            key={runCase.testCaseId}
            projectKey={projectKey}
            runCase={runCase}
            runStatus={run.status}
          />
        );
      })}
    </ul>
  );
};
