"use client";

import { DSEmptyState, DSErrorState, DSSkeleton, DSText } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { TestCaseDetail } from "@/modules/test-cases/typing/types/test-case.type";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useId, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { usePutReviewCommentResolve } from "../../hooks/mutations/use-put-review-comment-resolve";
import { useGetReviewComments } from "../../hooks/queries/use-get-review-comments";
import type { ReviewComment } from "../../typing/types/review-comment.type";
import { groupReviewComments } from "../../utils/review-comment.util";
import { ReviewCommentForm } from "../review-comment-form/review-comment-form";
import { ReviewCommentItem } from "../review-comment-item/review-comment-item";
import styles from "./review-comments-panel.module.scss";

interface Props {
  detail: TestCaseDetail;
  canComment: boolean;
}

export const ReviewCommentsPanel: FC<Props> = ({ detail, canComment }) => {
  const { t } = useTranslation("caseReview");
  const project = useCurrentProject();
  const { showSuccessToast } = useShowToast();
  const openTitleId = useId();
  const resolvedTitleId = useId();
  const { data, isPending, isError, isFetching, refetch } = useGetReviewComments(
    project.key,
    detail.code,
  );
  const resolveComment = usePutReviewCommentResolve(project.key, detail.code);
  const isDeprecated = detail.status === "deprecated";

  const handleResolve = (commentId: string): void => {
    resolveComment.mutate(commentId, {
      onSuccess: () => {
        showSuccessToast(t("comments.resolved"));
      },
    });
  };

  const renderList = (comments: readonly ReviewComment[]): ReactNode => {
    return (
      <ul className={styles.list}>
        {comments.map((comment) => {
          return (
            <ReviewCommentItem
              key={comment.id}
              comment={comment}
              currentVersionNumber={detail.currentVersion.number}
              canResolve={canComment}
              isResolving={resolveComment.isPending && resolveComment.variables === comment.id}
              onResolve={handleResolve}
            />
          );
        })}
      </ul>
    );
  };

  if (isPending) {
    return (
      <div aria-busy="true">
        <DSSkeleton lineCount={5} />
      </div>
    );
  }

  if (isError || data === undefined) {
    return (
      <DSErrorState
        title={t("comments.loadError")}
        retryLabel={t("retry")}
        isRetrying={isFetching}
        onRetry={() => {
          void refetch();
        }}
      />
    );
  }

  const { open, resolved } = groupReviewComments(data);

  return (
    <div className={styles.panel}>
      {canComment && !isDeprecated && <ReviewCommentForm detail={detail} />}
      {canComment && isDeprecated && <DSText color="muted">{t("comments.deprecated")}</DSText>}
      <section aria-labelledby={openTitleId} className={styles.section}>
        <h2 id={openTitleId} className={styles.heading}>
          {t("comments.openTitle", { count: open.length })}
        </h2>
        {open.length === 0 ? (
          <DSEmptyState
            title={t("comments.emptyTitle")}
            description={t("comments.emptyDescription")}
            icon="comment"
            size="sm"
            titleOrder={3}
          />
        ) : (
          renderList(open)
        )}
      </section>
      {resolved.length > 0 && (
        <section aria-labelledby={resolvedTitleId} className={styles.section}>
          <h2 id={resolvedTitleId} className={styles.heading}>
            {t("comments.resolvedTitle", { count: resolved.length })}
          </h2>
          {renderList(resolved)}
        </section>
      )}
    </div>
  );
};
