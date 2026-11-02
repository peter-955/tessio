"use client";

import { DSAlert, DSButton } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { TestCaseDetail } from "@/modules/test-cases/typing/types/test-case.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetReviewComments } from "../../hooks/queries/use-get-review-comments";
import { useIsAuthorReviewBlocked } from "../../hooks/use-is-author-review-blocked";
import { countOpenReviewComments } from "../../utils/review-comment.util";
import styles from "./review-status-notice.module.scss";

interface Props {
  detail: TestCaseDetail;
  canEdit: boolean;
  onShowComments: () => void;
}

export const ReviewStatusNotice: FC<Props> = ({ detail, canEdit, onShowComments }) => {
  const { t } = useTranslation("caseReview");
  const project = useCurrentProject();
  const { data } = useGetReviewComments(project.key, detail.code);
  const isAuthorBlocked = useIsAuthorReviewBlocked(detail);
  const openCount = countOpenReviewComments(data);
  const isInReview = detail.status === "in_review";
  const isOpenShown = isInReview && openCount > 0;
  const isAuthorShown = canEdit && isAuthorBlocked && (isInReview || detail.needsReview);

  if (!isOpenShown && !isAuthorShown) {
    return null;
  }

  return (
    <div className={styles.notices}>
      {isOpenShown && (
        <DSAlert
          color="warning"
          action={
            <DSButton type="default" size="sm" icon="comment" onClick={onShowComments}>
              {t("notice.showComments")}
            </DSButton>
          }
        >
          {t("notice.openComments", { count: openCount })}
        </DSAlert>
      )}
      {isAuthorShown && (
        <DSAlert color="info">
          {t("notice.separateReviewer", { number: detail.currentVersion.number })}
        </DSAlert>
      )}
    </div>
  );
};
