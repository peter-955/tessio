"use client";

import { DSActionIcon, DSBadge, DSMenu, DSText, type DSMenuItem } from "@/components/design-system";
import { buildCasePath, buildStoryPath } from "@/modules/runs/utils/run-path.util";
import { TestCasePriorityBadge } from "@/modules/test-cases/components/test-case-priority-badge/test-case-priority-badge";
import { TestCaseStatusBadge } from "@/modules/test-cases/components/test-case-status-badge/test-case-status-badge";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { SuiteCase } from "../../typing/types/suite.type";
import styles from "./suite-case-row.module.scss";

interface Props {
  projectKey: string;
  suiteCase: SuiteCase;
  index: number;
  total: number;
  canEdit: boolean;
  onMove: (fromIndex: number, toIndex: number) => void;
  onRemove: (suiteCase: SuiteCase) => void;
}

export const SuiteCaseRow: FC<Props> = ({
  projectKey,
  suiteCase,
  index,
  total,
  canEdit,
  onMove,
  onRemove,
}) => {
  const { t } = useTranslation("suites");
  const isFirst = index === 0;
  const isLast = index === total - 1;
  const menuItems: DSMenuItem[] = [
    {
      key: "moveUp",
      label: t("cases.moveUp"),
      isDisabled: isFirst,
      onClick: () => {
        onMove(index, index - 1);
      },
    },
    {
      key: "moveDown",
      label: t("cases.moveDown"),
      isDisabled: isLast,
      onClick: () => {
        onMove(index, index + 1);
      },
    },
    {
      key: "moveToTop",
      label: t("cases.moveToTop"),
      isDisabled: isFirst,
      onClick: () => {
        onMove(index, 0);
      },
    },
    {
      key: "moveToBottom",
      label: t("cases.moveToBottom"),
      isDisabled: isLast,
      onClick: () => {
        onMove(index, total - 1);
      },
    },
    { key: "divider", type: "divider" },
    {
      key: "remove",
      label: t("cases.remove"),
      icon: "trash",
      isDanger: true,
      onClick: () => {
        onRemove(suiteCase);
      },
    },
  ];

  return (
    <div className={styles.row}>
      <div className={styles.main}>
        <div className={styles.heading}>
          <Link href={buildCasePath(projectKey, suiteCase.code)} className={styles.code}>
            {suiteCase.code}
          </Link>
          <DSText weight="medium" component="span" className={styles.title}>
            {suiteCase.title}
          </DSText>
        </div>
        <div className={styles.meta}>
          <Link href={buildStoryPath(projectKey, suiteCase.storyJiraKey)} className={styles.story}>
            {`${suiteCase.storyJiraKey} · ${suiteCase.storyTitle}`}
          </Link>
          <TestCaseStatusBadge status={suiteCase.status} />
          <TestCasePriorityBadge priority={suiteCase.priority} />
          {suiteCase.isNeedingReview && (
            <DSBadge color="yellow">{t("skipReason.needs_review")}</DSBadge>
          )}
          {!suiteCase.isRunnable && (
            <DSText size="xs" color="muted" component="span">
              {t("cases.skipped")}
            </DSText>
          )}
        </div>
      </div>
      {canEdit && (
        <DSMenu
          target={
            <DSActionIcon icon="dots" ariaLabel={t("cases.actionsFor", { code: suiteCase.code })} />
          }
          items={menuItems}
        />
      )}
    </div>
  );
};
