"use client";

import { DSSortableList, type DSSortableListItem } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { SuiteCase } from "../../typing/types/suite.type";
import { SuiteCaseRow } from "../suite-case-row/suite-case-row";
import styles from "./suite-case-list.module.scss";

interface Props {
  projectKey: string;
  cases: SuiteCase[];
  canEdit: boolean;
  isSaving: boolean;
  onMove: (fromIndex: number, toIndex: number) => void;
  onRemove: (suiteCase: SuiteCase) => void;
}

export const SuiteCaseList: FC<Props> = ({
  projectKey,
  cases,
  canEdit,
  isSaving,
  onMove,
  onRemove,
}) => {
  const { t } = useTranslation("suites");

  const renderRow = (suiteCase: SuiteCase, index: number): DSSortableListItem => {
    return {
      key: suiteCase.testCaseId,
      content: (
        <SuiteCaseRow
          projectKey={projectKey}
          suiteCase={suiteCase}
          index={index}
          total={cases.length}
          canEdit={canEdit}
          onMove={onMove}
          onRemove={onRemove}
        />
      ),
    };
  };

  if (!canEdit) {
    return (
      <ol className={styles.list} aria-label={t("cases.listLabel")}>
        {cases.map((suiteCase, index) => {
          return (
            <li key={suiteCase.testCaseId} className={styles.item}>
              {renderRow(suiteCase, index).content}
            </li>
          );
        })}
      </ol>
    );
  }

  return (
    <div aria-busy={isSaving}>
      <DSSortableList
        items={cases.map(renderRow)}
        onMove={onMove}
        labels={{
          list: t("cases.listLabel"),
          handle: (position) => {
            return t("cases.handle", { code: cases[position - 1]?.code ?? position });
          },
          instructions: t("cases.instructions"),
          moved: (position, total) => {
            return t("cases.moved", { position, total });
          },
        }}
      />
    </div>
  );
};
