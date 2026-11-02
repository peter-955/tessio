"use client";

import { DSText } from "@/components/design-system";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import type {
  StepDiff,
  TextDiffLabels,
  VersionDiffEntry,
} from "../../typing/types/version-diff.type";
import { TestCasePriorityBadge } from "../test-case-priority-badge/test-case-priority-badge";
import { TextDiff } from "../text-diff/text-diff";
import styles from "./version-diff.module.scss";

interface Props {
  entries: readonly VersionDiffEntry[];
}

const ARROW = "→";

const CODE_SEPARATOR = " ";

export const VersionDiff: FC<Props> = ({ entries }) => {
  const { t } = useTranslation("testCases");
  const diffLabels: TextDiffLabels = {
    added: t("history.diffAdded"),
    removed: t("history.diffRemoved"),
  };

  if (entries.length === 0) {
    return <DSText color="muted">{t("history.identical")}</DSText>;
  }

  const describeStep = (step: StepDiff): string => {
    switch (step.change) {
      case "added":
        return t("history.stepAdded", { position: step.position });
      case "removed":
        return t("history.stepRemoved", { position: step.position });
      case "changed":
        return t("history.stepChanged", { position: step.position });
    }
  };

  const renderEntry = (entry: VersionDiffEntry): ReactNode => {
    switch (entry.kind) {
      case "text":
        return <TextDiff tokens={entry.tokens} labels={diffLabels} />;
      case "priority":
        return (
          <span className={styles.priority}>
            <TestCasePriorityBadge priority={entry.from} />
            <span aria-hidden="true">{ARROW}</span>
            <TestCasePriorityBadge priority={entry.to} />
          </span>
        );
      case "criteria":
        return <TextDiff tokens={entry.tokens} separator={CODE_SEPARATOR} labels={diffLabels} />;
      case "dataTable":
        return <TextDiff tokens={entry.tokens} labels={diffLabels} />;
      case "files":
        return (
          <DSText size="sm">
            {t("history.filesChanged", { added: entry.added, removed: entry.removed })}
          </DSText>
        );
      case "steps":
        return (
          <ul className={styles.steps}>
            {entry.steps.map((step) => {
              return (
                <li key={step.position} className={styles.step}>
                  <span className={styles.stepTitle}>{describeStep(step)}</span>
                  <div className={styles.stepPart}>
                    <span className={styles.muted}>{t("history.stepAction")}</span>
                    <TextDiff tokens={step.action} labels={diffLabels} />
                  </div>
                  <div className={styles.stepPart}>
                    <span className={styles.muted}>{t("history.stepExpected")}</span>
                    <TextDiff tokens={step.expected} labels={diffLabels} />
                  </div>
                </li>
              );
            })}
          </ul>
        );
    }
  };

  return (
    <dl className={styles.list}>
      {entries.map((entry) => {
        return (
          <div key={entry.field} className={styles.entry}>
            <dt className={styles.field}>{t(`history.fields.${entry.field}`)}</dt>
            <dd className={styles.value}>{renderEntry(entry)}</dd>
          </div>
        );
      })}
    </dl>
  );
};
