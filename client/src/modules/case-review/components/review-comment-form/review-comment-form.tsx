"use client";

import {
  DSButton,
  DSGroup,
  DSSelect,
  DSStack,
  DSTextarea,
  type DSSelectOption,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { TestCaseDetail } from "@/modules/test-cases/typing/types/test-case.type";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC, type FormEvent } from "react";
import { useTranslation } from "react-i18next";
import { usePostReviewComment } from "../../hooks/mutations/use-post-review-comment";
import {
  MAX_REVIEW_COMMENT_LENGTH,
  STEP_OPTION_TEXT_LENGTH,
  WHOLE_CASE_TARGET,
} from "../../typing/constants/review-comment.constant";
import { parseStepTarget, truncateText } from "../../utils/review-comment.util";

interface Props {
  detail: TestCaseDetail;
}

export const ReviewCommentForm: FC<Props> = ({ detail }) => {
  const { t } = useTranslation("caseReview");
  const { t: tSharedSteps } = useTranslation("sharedSteps");
  const project = useCurrentProject();
  const { showSuccessToast } = useShowToast();
  const [target, setTarget] = useState(WHOLE_CASE_TARGET);
  const [body, setBody] = useState("");
  const [error, setError] = useState<string | null>(null);
  const postComment = usePostReviewComment(project.key, detail.code);
  const steps = [...detail.currentVersion.steps].sort((first, second) => {
    return first.order - second.order;
  });
  const targetOptions: DSSelectOption<string>[] = [
    { value: WHOLE_CASE_TARGET, label: t("comments.wholeCase") },
    ...steps.map((step): DSSelectOption<string> => {
      return {
        value: String(step.order),
        label: t("comments.stepOption", {
          order: step.order,
          action: truncateText(
            step.action ?? tSharedSteps("reference.textLabel", { key: step.sharedStepKey ?? "" }),
            STEP_OPTION_TEXT_LENGTH,
          ),
        }),
      };
    }),
  ];
  const selectedTarget = targetOptions.some((option) => option.value === target)
    ? target
    : WHOLE_CASE_TARGET;

  const handleSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    const trimmedBody = body.trim();
    if (trimmedBody === "") {
      setError(t("comments.bodyRequired"));
      return;
    }

    postComment.mutate(
      {
        body: trimmedBody,
        stepOrder: parseStepTarget(selectedTarget),
        versionNumber: detail.currentVersion.number,
      },
      {
        onSuccess: () => {
          setBody("");
          setTarget(WHOLE_CASE_TARGET);
          showSuccessToast(t("comments.added"));
        },
      },
    );
  };

  return (
    <form onSubmit={handleSubmit} noValidate aria-label={t("comments.formLabel")}>
      <DSStack gap={3}>
        <DSSelect<string>
          label={t("comments.target")}
          value={selectedTarget}
          options={targetOptions}
          onChange={(value) => {
            setTarget(value ?? WHOLE_CASE_TARGET);
          }}
          description={t("comments.targetDescription", {
            number: detail.currentVersion.number,
          })}
        />
        <DSTextarea
          label={t("comments.body")}
          value={body}
          onChange={(value) => {
            setBody(value);
            if (error !== null && value.trim() !== "") {
              setError(null);
            }
          }}
          placeholder={t("comments.bodyPlaceholder")}
          error={error}
          maxLength={MAX_REVIEW_COMMENT_LENGTH}
          isRequired
        />
        <DSGroup justify="end">
          <DSButton
            type="primary"
            nativeType="submit"
            icon="comment"
            isLoading={postComment.isPending}
          >
            {t("comments.add")}
          </DSButton>
        </DSGroup>
      </DSStack>
    </form>
  );
};
