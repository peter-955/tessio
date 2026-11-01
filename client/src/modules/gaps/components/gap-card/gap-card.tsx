"use client";

import { DSBadge, DSButton, DSCard, DSGroup, DSStack, DSText } from "@/components/design-system";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { GAP_SEVERITY_COLORS, GAP_STATUS_COLORS } from "../../typing/constants/gap.constant";
import type { Gap, GapAction } from "../../typing/types/gap.type";
import { describeAssignee } from "../../utils/gap-assignee.util";
import { buildStoryGapsHref } from "../../utils/gap-path.util";
import styles from "./gap-card.module.scss";

interface Props {
  gap: Gap;
  isInboxContext: boolean;
  canAnswer: boolean;
  canReassign: boolean;
  canReopen: boolean;
  onAction: (gap: Gap, action: GapAction) => void;
}

export const GapCard: FC<Props> = ({
  gap,
  isInboxContext,
  canAnswer,
  canReassign,
  canReopen,
  onAction,
}) => {
  const { t } = useTranslation("gaps");
  const formatDate = useFormatDate();
  const assignee = describeAssignee(gap);
  const isOpen = gap.status === "open";
  const isAnswerShown = isOpen && canAnswer;
  const isReassignShown = isOpen && canReassign;
  const targetLabel =
    gap.targetType === "story" || gap.targetRef === null
      ? t(`target.${gap.targetType}`)
      : gap.targetRef;

  const renderTime = (isoDate: string): ReactNode => {
    return (
      <>
        {" · "}
        <time dateTime={isoDate}>{formatDate(isoDate)}</time>
      </>
    );
  };

  const renderAssignee = (): ReactNode => {
    if (assignee.kind === "user") {
      return (
        <>
          <DSText size="sm" component="span" className={styles.wrapping}>
            {t("card.assignedTo", { name: assignee.name })}
          </DSText>
          {assignee.isDeactivated && <DSBadge color="red">{t("badge.deactivated")}</DSBadge>}
        </>
      );
    }

    if (assignee.kind === "role") {
      return (
        <DSText size="sm" component="span">
          {t("card.assignedToRole", { role: t(`roles.${assignee.role}`) })}
        </DSText>
      );
    }

    return (
      <DSText size="sm" color="muted" component="span">
        {t("card.unassigned")}
      </DSText>
    );
  };

  return (
    <li className={styles.item}>
      <DSCard className={styles.card}>
        <DSStack gap={3}>
          {isInboxContext && (
            <div className={styles.context}>
              <DSText size="sm" color="muted" component="span" className={styles.wrapping}>
                {gap.projectName}
              </DSText>
              <Link
                href={buildStoryGapsHref(gap.projectKey, gap.storyJiraKey)}
                prefetch={false}
                className={styles.storyLink}
              >
                {`${gap.storyJiraKey} · ${gap.storyTitle}`}
              </Link>
            </div>
          )}
          <DSGroup gap={2} isWrapping>
            <DSBadge color={GAP_SEVERITY_COLORS[gap.severity]}>
              {t(`severity.${gap.severity}`)}
            </DSBadge>
            <DSBadge>{t(`type.${gap.type}`)}</DSBadge>
            <DSBadge>{targetLabel}</DSBadge>
            <DSBadge color={GAP_STATUS_COLORS[gap.status]} hasDot>
              {t(`status.${gap.status}`)}
            </DSBadge>
            {gap.isRaisedViaClaude && <DSBadge color="tessio">{t("badge.viaClaude")}</DSBadge>}
          </DSGroup>
          <DSText className={styles.question}>{gap.question}</DSText>
          <DSText size="xs" color="muted" className={styles.wrapping}>
            {t("card.raisedBy", { name: gap.raisedByName })}
            {renderTime(gap.createdAt)}
            {gap.dataScope !== null &&
              ` · ${t("dataScope.label")}: ${t(`dataScope.${gap.dataScope}`)}`}
          </DSText>
          <DSStack gap={1}>
            <DSGroup gap={2} isWrapping>
              {renderAssignee()}
            </DSGroup>
            {assignee.kind === "user" && assignee.isDeactivated && isOpen && (
              <DSText size="sm" color="warning">
                {t("card.reassignHint")}
              </DSText>
            )}
          </DSStack>
          {gap.status === "resolved" && gap.answer !== null && (
            <div className={styles.answer}>
              <DSText size="sm" className={styles.question}>
                {gap.answer}
              </DSText>
              {gap.answeredByName !== null && gap.answeredAt !== null && (
                <DSText size="xs" color="muted" className={styles.wrapping}>
                  {t("card.answeredBy", { name: gap.answeredByName })}
                  {renderTime(gap.answeredAt)}
                </DSText>
              )}
            </div>
          )}
          {gap.reopenedAt !== null && gap.reopenedByName !== null && (
            <DSText size="xs" color="muted" className={styles.wrapping}>
              {t("card.reopenedBy", { name: gap.reopenedByName })}
              {renderTime(gap.reopenedAt)}
            </DSText>
          )}
          {(isAnswerShown || isReassignShown || canReopen) && (
            <DSGroup gap={2} isWrapping>
              {isAnswerShown && (
                <DSButton
                  type="primary"
                  size="sm"
                  icon="check"
                  onClick={() => {
                    onAction(gap, "answer");
                  }}
                >
                  {t("actions.answer")}
                </DSButton>
              )}
              {isReassignShown && (
                <DSButton
                  type="default"
                  size="sm"
                  icon="members"
                  onClick={() => {
                    onAction(gap, "reassign");
                  }}
                >
                  {t("actions.reassign")}
                </DSButton>
              )}
              {canReopen && (
                <DSButton
                  type="outline"
                  size="sm"
                  icon="restore"
                  onClick={() => {
                    onAction(gap, "reopen");
                  }}
                >
                  {t("actions.reopen")}
                </DSButton>
              )}
            </DSGroup>
          )}
        </DSStack>
      </DSCard>
    </li>
  );
};
