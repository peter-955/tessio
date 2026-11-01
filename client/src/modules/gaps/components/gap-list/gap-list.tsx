"use client";

import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import type { Gap, GapAction, GapActionTarget } from "../../typing/types/gap.type";
import { AnswerGapModal } from "../answer-gap-modal/answer-gap-modal";
import { GapCard } from "../gap-card/gap-card";
import { ReassignGapModal } from "../reassign-gap-modal/reassign-gap-modal";
import { ReopenGapModal } from "../reopen-gap-modal/reopen-gap-modal";
import styles from "./gap-list.module.scss";

interface Props {
  gaps: Gap[];
  isInboxContext: boolean;
  canAnswer: boolean;
  canReassign: boolean;
  checkCanReopen: (gap: Gap) => boolean;
}

export const GapList: FC<Props> = ({
  gaps,
  isInboxContext,
  canAnswer,
  canReassign,
  checkCanReopen,
}) => {
  const { t } = useTranslation("gaps");
  const [actionTarget, setActionTarget] = useState<GapActionTarget | null>(null);

  const handleAction = (gap: Gap, action: GapAction): void => {
    setActionTarget({ gap, action });
  };

  const handleClose = (): void => {
    setActionTarget(null);
  };

  return (
    <>
      <ul className={styles.list} aria-label={t("tab.listLabel")}>
        {gaps.map((gap) => {
          return (
            <GapCard
              key={gap.id}
              gap={gap}
              isInboxContext={isInboxContext}
              canAnswer={canAnswer}
              canReassign={canReassign}
              canReopen={checkCanReopen(gap)}
              onAction={handleAction}
            />
          );
        })}
      </ul>
      {actionTarget?.action === "answer" && (
        <AnswerGapModal gap={actionTarget.gap} onClose={handleClose} />
      )}
      {actionTarget?.action === "reassign" && (
        <ReassignGapModal gap={actionTarget.gap} onClose={handleClose} />
      )}
      {actionTarget?.action === "reopen" && (
        <ReopenGapModal gap={actionTarget.gap} onClose={handleClose} />
      )}
    </>
  );
};
