"use client";

import type { CaseReferences } from "@/components/case-sheet/typing/types/case-sheet.type";
import { DSText, DSTitle } from "@/components/design-system";
import { SuspectedCause } from "@/components/suspected-cause/suspected-cause";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { ManualRunCase } from "../../typing/types/manual-run.type";
import { RecordedSteps } from "../recorded-steps/recorded-steps";
import { ResultStatusBadge } from "../result-status-badge/result-status-badge";
import styles from "./recorded-case-view.module.scss";

interface Props {
  runCase: ManualRunCase;
  references: CaseReferences;
}

export const RecordedCaseView: FC<Props> = ({ runCase, references }) => {
  const { t } = useTranslation("manualRun");

  return (
    <section className={styles.view} aria-label={`${runCase.code} · ${runCase.title}`}>
      <div className={styles.header}>
        <DSTitle order={2} type="section" className={styles.title}>
          {`${runCase.code} · ${runCase.title}`}
        </DSTitle>
        {runCase.result === null ? (
          <DSText size="sm" color="muted" component="span">
            {t("record.notRecorded")}
          </DSText>
        ) : (
          <ResultStatusBadge status={runCase.result.status} />
        )}
      </div>
      {runCase.result !== null && runCase.result.suspectedCause !== null && (
        <SuspectedCause cause={runCase.result.suspectedCause} reason={runCase.result.causeReason} />
      )}
      <RecordedSteps
        steps={runCase.steps}
        references={references}
        ariaLabel={t("record.stepsOf", { code: runCase.code })}
      />
    </section>
  );
};
