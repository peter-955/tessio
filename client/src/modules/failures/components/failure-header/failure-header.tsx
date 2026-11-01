"use client";

import { DSButton, DSButtonLink, DSPageHeader } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { buildStoryPath } from "@/modules/stories/utils/story-path.util";
import { buildTestCasePath } from "@/modules/test-cases/utils/test-case-path.util";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import type { FailureDetail } from "../../typing/types/failure.type";
import { buildFailureStatusActions } from "../../utils/failure-actions.util";
import { checkCanAssignFailure } from "../../utils/failure-capability.util";
import { buildFailureRunPath, buildFailuresPath } from "../../utils/failure-path.util";
import { AssignFailureModal } from "../assign-failure-modal/assign-failure-modal";
import { FailureAssignee } from "../failure-assignee/failure-assignee";
import { FailureStatusActions } from "../failure-status-actions/failure-status-actions";
import { FailureStatusBadge } from "../failure-status-badge/failure-status-badge";
import styles from "./failure-header.module.scss";

interface Props {
  failure: FailureDetail;
}

export const FailureHeader: FC<Props> = ({ failure }) => {
  const { t } = useTranslation("failures");
  const project = useCurrentProject();
  const formatDate = useFormatDate();
  const [isAssignOpened, setIsAssignOpened] = useState(false);
  const canAssign = checkCanAssignFailure(project, failure);
  const hasActions = canAssign || buildFailureStatusActions(failure.status, project).length > 0;

  return (
    <>
      <div className={styles.back}>
        <DSButtonLink href={buildFailuresPath(project.key)} type="ghost">
          {t("detail.back")}
        </DSButtonLink>
      </div>
      <DSPageHeader
        title={`${failure.testCaseCode} · ${failure.testCaseTitle}`}
        description={
          <span className={styles.details}>
            <FailureStatusBadge status={failure.status} />
            <Link href={buildStoryPath(project.key, failure.storyJiraKey)}>
              {`${failure.storyJiraKey} · ${failure.storyTitle}`}
            </Link>
            <Link href={buildTestCasePath(project.key, failure.testCaseCode)}>
              {failure.testCaseCode}
            </Link>
            <FailureAssignee failure={failure} />
            <span>{t("detail.opened", { date: formatDate(failure.createdAt) })}</span>
            <Link href={buildFailureRunPath(project.key, failure.latestRunId)}>
              {t("detail.lastFailed", { date: formatDate(failure.latestFailedAt) })}
            </Link>
            {failure.statusChangedAt !== null && failure.statusChangedByName !== null && (
              <span>
                {t("detail.statusChangedBy", {
                  name: failure.statusChangedByName,
                  date: formatDate(failure.statusChangedAt),
                })}
              </span>
            )}
          </span>
        }
        actions={
          hasActions && (
            <>
              <FailureStatusActions failure={failure} />
              {canAssign && (
                <DSButton
                  type="default"
                  icon="user"
                  onClick={() => {
                    setIsAssignOpened(true);
                  }}
                >
                  {failure.assigneeId === null ? t("actions.assign") : t("actions.reassign")}
                </DSButton>
              )}
            </>
          )
        }
      />
      {isAssignOpened && (
        <AssignFailureModal
          failure={failure}
          onClose={() => {
            setIsAssignOpened(false);
          }}
        />
      )}
    </>
  );
};
