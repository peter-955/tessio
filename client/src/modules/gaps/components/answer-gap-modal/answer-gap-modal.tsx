"use client";

import { DSModal, DSStack, DSText, DSTextarea } from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC, type FormEvent } from "react";
import { useTranslation } from "react-i18next";
import { usePutGapAnswer } from "../../hooks/mutations/use-put-gap-answer";
import { ANSWER_GAP_FORM_ID, MAX_ANSWER_LENGTH } from "../../typing/constants/gap.constant";
import type { Gap } from "../../typing/types/gap.type";
import styles from "./answer-gap-modal.module.scss";

interface Props {
  gap: Gap;
  onClose: () => void;
}

export const AnswerGapModal: FC<Props> = ({ gap, onClose }) => {
  const { t } = useTranslation("gaps");
  const { showSuccessToast } = useShowToast();
  const answerGap = usePutGapAnswer();
  const [answer, setAnswer] = useState("");
  const trimmedAnswer = answer.trim();

  const handleSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    if (trimmedAnswer === "") {
      return;
    }

    answerGap.mutate(
      { projectKey: gap.projectKey, gapId: gap.id, answer: trimmedAnswer },
      {
        onSuccess: () => {
          showSuccessToast(t("toasts.answered"));
          onClose();
        },
        onError: (error: ApiError) => {
          if (error.code === "GAP_NOT_OPEN") {
            onClose();
          }
        },
      },
    );
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("answer.title")}
      isCloseDisabled={answerGap.isPending}
      action={{
        label: t("answer.submit"),
        icon: "check",
        formId: ANSWER_GAP_FORM_ID,
        isLoading: answerGap.isPending,
        isDisabled: trimmedAnswer === "",
      }}
    >
      <form id={ANSWER_GAP_FORM_ID} onSubmit={handleSubmit} noValidate>
        <DSStack gap={4}>
          <DSText className={styles.question}>{gap.question}</DSText>
          <DSTextarea
            label={t("answer.label")}
            value={answer}
            onChange={setAnswer}
            maxLength={MAX_ANSWER_LENGTH}
            isRequired
            isAutosize
          />
        </DSStack>
      </form>
    </DSModal>
  );
};
