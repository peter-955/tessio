"use client";

import { DSTable } from "@/components/design-system";
import { buildStoryPath } from "@/modules/stories/utils/story-path.util";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { Failure } from "../../typing/types/failure.type";
import { buildFailurePath, buildFailureRunPath } from "../../utils/failure-path.util";
import { FailureAssignee } from "../failure-assignee/failure-assignee";
import { FailureStatusBadge } from "../failure-status-badge/failure-status-badge";
import styles from "./failure-table.module.scss";

interface Props {
  projectKey: string;
  failures: Failure[];
}

export const FailureTable: FC<Props> = ({ projectKey, failures }) => {
  const { t } = useTranslation("failures");
  const formatDate = useFormatDate();

  return (
    <DSTable label={t("title")}>
      <caption className={styles.caption}>{t("title")}</caption>
      <thead>
        <tr>
          <th scope="col">{t("columns.testCase")}</th>
          <th scope="col">{t("columns.story")}</th>
          <th scope="col">{t("columns.status")}</th>
          <th scope="col">{t("columns.assignee")}</th>
          <th scope="col">{t("columns.lastFailed")}</th>
        </tr>
      </thead>
      <tbody>
        {failures.map((failure) => {
          return (
            <tr key={failure.id}>
              <td className={styles.testCase}>
                <Link href={buildFailurePath(projectKey, failure.id)}>
                  {`${failure.testCaseCode} · ${failure.testCaseTitle}`}
                </Link>
              </td>
              <td>
                <Link href={buildStoryPath(projectKey, failure.storyJiraKey)}>
                  {failure.storyJiraKey}
                </Link>
              </td>
              <td>
                <FailureStatusBadge status={failure.status} />
              </td>
              <td>
                <FailureAssignee failure={failure} />
              </td>
              <td>
                <Link href={buildFailureRunPath(projectKey, failure.latestRunId)}>
                  {formatDate(failure.latestFailedAt)}
                </Link>
              </td>
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
