"use client";

import { DSButtonLink, DSPageHeader } from "@/components/design-system";
import { buildStoryPath } from "@/modules/stories/utils/story-path.util";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { TestCaseDetail } from "../../typing/types/test-case.type";
import { buildTestCasesPath } from "../../utils/test-case-path.util";
import { TestCasePriorityBadge } from "../test-case-priority-badge/test-case-priority-badge";
import { TestCaseStatusActions } from "../test-case-status-actions/test-case-status-actions";
import { TestCaseStatusBadge } from "../test-case-status-badge/test-case-status-badge";
import styles from "./test-case-header.module.scss";

interface Props {
  projectKey: string;
  detail: TestCaseDetail;
  isDirty: boolean;
  canEdit: boolean;
}

export const TestCaseHeader: FC<Props> = ({ projectKey, detail, isDirty, canEdit }) => {
  const { t } = useTranslation("testCases");

  return (
    <>
      <div className={styles.back}>
        <DSButtonLink href={buildTestCasesPath(projectKey)} type="ghost">
          {t("actions.back")}
        </DSButtonLink>
      </div>
      <DSPageHeader
        title={`${detail.code} · ${detail.title}`}
        description={
          <span className={styles.details}>
            <TestCaseStatusBadge status={detail.status} />
            <TestCasePriorityBadge priority={detail.priority} />
            <Link href={buildStoryPath(projectKey, detail.story.jiraKey)}>
              {`${detail.story.jiraKey} · ${detail.story.title}`}
            </Link>
            <span>{t("detail.version", { number: detail.currentVersion.number })}</span>
          </span>
        }
        actions={canEdit && <TestCaseStatusActions detail={detail} isDirty={isDirty} />}
      />
    </>
  );
};
