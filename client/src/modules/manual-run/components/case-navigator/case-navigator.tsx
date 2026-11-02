"use client";

import { DSSelect, DSText, type DSSelectOption } from "@/components/design-system";
import classNames from "classnames";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { ManualRunCase } from "../../typing/types/manual-run.type";
import {
  checkIsCaseRecorded,
  checkIsDataDrivenCase,
  countRecordedIterations,
} from "../../utils/run-case.util";
import { ResultStatusBadge } from "../result-status-badge/result-status-badge";
import styles from "./case-navigator.module.scss";

interface Props {
  cases: ManualRunCase[];
  currentTestCaseId: string;
  onSelect: (testCaseId: string) => void;
}

export const CaseNavigator: FC<Props> = ({ cases, currentTestCaseId, onSelect }) => {
  const { t } = useTranslation("manualRun");
  const { t: tDataRows } = useTranslation("dataRows");

  const readPendingLabel = (runCase: ManualRunCase): string => {
    return checkIsDataDrivenCase(runCase)
      ? tDataRows("iteration.summary", {
          count: runCase.iterations.length,
          recorded: countRecordedIterations(runCase),
        })
      : t("record.notRecorded");
  };

  const options = cases.map((runCase): DSSelectOption<string> => {
    const statusLabel =
      runCase.result === null || !checkIsCaseRecorded(runCase)
        ? readPendingLabel(runCase)
        : t(`status.${runCase.result.status}`);

    return {
      value: runCase.testCaseId,
      label: `${runCase.code} · ${runCase.title} · ${statusLabel}`,
    };
  });

  const handleSelectChange = (testCaseId: string | null): void => {
    if (testCaseId !== null) {
      onSelect(testCaseId);
    }
  };

  return (
    <>
      <nav className={styles.list} aria-label={t("record.caseList")}>
        <DSText size="sm" weight="medium" component="span" className={styles.heading}>
          {t("record.caseList")}
        </DSText>
        <ul className={styles.items}>
          {cases.map((runCase) => {
            const isCurrent = runCase.testCaseId === currentTestCaseId;

            return (
              <li key={runCase.testCaseId}>
                <button
                  type="button"
                  className={classNames(styles.item, isCurrent && styles.current)}
                  aria-current={isCurrent ? "true" : undefined}
                  onClick={() => {
                    onSelect(runCase.testCaseId);
                  }}
                >
                  <span className={styles.code}>{runCase.code}</span>
                  <span className={styles.title}>{runCase.title}</span>
                  <span className={styles.status}>
                    {runCase.result === null || !checkIsCaseRecorded(runCase) ? (
                      <DSText size="xs" color="muted" component="span">
                        {readPendingLabel(runCase)}
                      </DSText>
                    ) : (
                      <ResultStatusBadge status={runCase.result.status} />
                    )}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>
      <div className={styles.select}>
        <DSSelect<string>
          label={t("record.caseList")}
          value={currentTestCaseId}
          options={options}
          onChange={handleSelectChange}
        />
      </div>
    </>
  );
};
