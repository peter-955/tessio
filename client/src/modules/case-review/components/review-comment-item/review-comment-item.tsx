"use client";

import { DSBadge, DSButton, DSText } from "@/components/design-system";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { ReviewComment } from "../../typing/types/review-comment.type";
import styles from "./review-comment-item.module.scss";

interface Props {
  comment: ReviewComment;
  currentVersionNumber: number;
  canResolve: boolean;
  isResolving: boolean;
  onResolve: (commentId: string) => void;
}

export const ReviewCommentItem: FC<Props> = ({
  comment,
  currentVersionNumber,
  canResolve,
  isResolving,
  onResolve,
}) => {
  const { t } = useTranslation("caseReview");
  const formatDate = useFormatDate();
  const target =
    comment.stepOrder === null
      ? t("comments.wholeCase")
      : t("comments.step", { order: comment.stepOrder });

  return (
    <li className={styles.item}>
      <div className={styles.header}>
        <span className={styles.author}>{comment.authorName}</span>
        <span className={styles.muted}>{formatDate(comment.createdAt)}</span>
        <DSBadge color="tessio">{target}</DSBadge>
        <DSBadge color={comment.versionNumber === currentVersionNumber ? "gray" : "yellow"}>
          {comment.versionNumber === currentVersionNumber
            ? t("comments.version", { number: comment.versionNumber })
            : t("comments.olderVersion", { number: comment.versionNumber })}
        </DSBadge>
      </div>
      <DSText className={styles.body}>{comment.body}</DSText>
      {comment.isResolved && comment.resolvedAt !== null && (
        <DSText size="sm" color="muted">
          {t("comments.resolvedBy", {
            name: comment.resolvedByName ?? t("comments.formerMember"),
            date: formatDate(comment.resolvedAt),
          })}
        </DSText>
      )}
      {!comment.isResolved && canResolve && (
        <div>
          <DSButton
            type="default"
            size="sm"
            icon="check"
            isLoading={isResolving}
            ariaLabel={t("comments.resolveLabel", { name: comment.authorName, target })}
            onClick={() => {
              onResolve(comment.id);
            }}
          >
            {t("comments.resolve")}
          </DSButton>
        </div>
      )}
    </li>
  );
};
