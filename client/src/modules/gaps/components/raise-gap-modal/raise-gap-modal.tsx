"use client";

import {
  DSModal,
  DSSegmentedControl,
  DSSelect,
  DSStack,
  DSText,
  DSTextarea,
  useDSForm,
  type DSSegmentedOption,
  type DSSelectOption,
} from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useGetStory } from "@/modules/stories/hooks/queries/use-get-story";
import { useGetProjectMembers } from "@/shared/hooks/queries/use-get-project-members";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useMemo, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostGap } from "../../hooks/mutations/use-post-gap";
import { useGetGapTestCaseOptions } from "../../hooks/queries/use-get-gap-test-case-options";
import {
  GAP_DATA_SCOPES,
  GAP_SEVERITIES,
  GAP_TARGET_TYPES,
  GAP_TYPES,
  MAX_QUESTION_LENGTH,
  MISSING_TEST_DATA_TYPE,
  RAISE_GAP_FORM_ID,
  RAISE_GAP_INITIAL_VALUES,
} from "../../typing/constants/gap.constant";
import type {
  GapDataScope,
  GapSeverity,
  GapTargetType,
  GapType,
} from "../../typing/types/gap.type";
import type { RaiseGapValues } from "../../typing/types/raise-gap-values.type";
import { buildMemberOptions } from "../../utils/assignee-options.util";
import { toFormErrorText } from "../../utils/form-error.util";
import { buildRaiseGapBody } from "../../utils/raise-gap-body.util";
import { buildCriterionOptions } from "../../utils/target-options.util";
import styles from "./raise-gap-modal.module.scss";

interface Props {
  projectKey: string;
  jiraKey: string;
  onClose: () => void;
}

export const RaiseGapModal: FC<Props> = ({ projectKey, jiraKey, onClose }) => {
  const { t } = useTranslation("gaps");
  const { showSuccessToast } = useShowToast();
  const story = useGetStory(projectKey, jiraKey);
  const members = useGetProjectMembers(projectKey);
  const raiseGap = usePostGap(projectKey, jiraKey);
  const form = useDSForm<RaiseGapValues>({
    mode: "controlled",
    initialValues: RAISE_GAP_INITIAL_VALUES,
    validate: {
      type: (value) => {
        return value === null ? t("errors.typeRequired") : null;
      },
      targetRef: (value, values) => {
        return values.targetType !== "story" && value === null ? t("errors.targetRequired") : null;
      },
      question: (value) => {
        return value.trim() === "" ? t("errors.questionRequired") : null;
      },
    },
  });
  const { targetType, type } = form.values;
  const testCaseOptions = useGetGapTestCaseOptions(projectKey, jiraKey, targetType === "test_case");
  const criterionOptions = useMemo((): DSSelectOption<string>[] => {
    return buildCriterionOptions(story.data?.criteria ?? []);
  }, [story.data]);
  const memberOptions = useMemo((): DSSelectOption<string>[] => {
    return buildMemberOptions(members.data ?? [], (role) => {
      return t(`roles.${role}`);
    });
  }, [members.data, t]);
  const targetOptions = targetType === "criterion" ? criterionOptions : testCaseOptions.options;
  const isTargetLoading = targetType === "criterion" ? story.isPending : testCaseOptions.isPending;
  const hasNoTargets = !isTargetLoading && targetOptions.length === 0;

  const typeOptions = GAP_TYPES.map((gapType): DSSelectOption<GapType> => {
    return { value: gapType, label: t(`type.${gapType}`) };
  });
  const severityOptions = GAP_SEVERITIES.map((severity): DSSegmentedOption<GapSeverity> => {
    return { value: severity, label: t(`severity.${severity}`) };
  });
  const targetTypeOptions = GAP_TARGET_TYPES.map(
    (gapTargetType): DSSegmentedOption<GapTargetType> => {
      return { value: gapTargetType, label: t(`target.${gapTargetType}`) };
    },
  );
  const dataScopeOptions = GAP_DATA_SCOPES.map((dataScope): DSSelectOption<GapDataScope> => {
    return { value: dataScope, label: t(`dataScope.${dataScope}`) };
  });

  const handleClose = (): void => {
    form.reset();
    raiseGap.reset();
    onClose();
  };

  const handleValidSubmit = (values: RaiseGapValues): void => {
    if (values.type === null) {
      return;
    }

    raiseGap.mutate(buildRaiseGapBody({ ...values, type: values.type }), {
      onSuccess: () => {
        showSuccessToast(t("toasts.raised"));
        handleClose();
      },
      onError: (error: ApiError) => {
        if (error.code === "UNKNOWN_REFERENCE") {
          form.setFieldError("targetRef", t("errors.unknownTarget"));
        }

        if (error.code === "ASSIGNEE_NOT_ACTIVE_MEMBER") {
          form.setFieldError("assigneeId", t("errors.assigneeNotActive"));
          void members.refetch();
        }
      },
    });
  };

  const handleTypeChange = (value: GapType | null): void => {
    form.setFieldValue("type", value);
    if (value !== MISSING_TEST_DATA_TYPE) {
      form.setFieldValue("dataScope", null);
    }
  };

  const handleTargetTypeChange = (value: GapTargetType): void => {
    form.setValues({ targetType: value, targetRef: null });
    form.clearFieldError("targetRef");
  };

  return (
    <DSModal
      isOpened
      onClose={handleClose}
      title={t("raise.title")}
      isCloseDisabled={raiseGap.isPending}
      action={{
        label: t("raise.submit"),
        icon: "plus",
        formId: RAISE_GAP_FORM_ID,
        isLoading: raiseGap.isPending,
      }}
    >
      <form id={RAISE_GAP_FORM_ID} onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
        <DSStack gap={4}>
          <DSSelect<GapType>
            label={t("raise.typeLabel")}
            value={type}
            options={typeOptions}
            onChange={handleTypeChange}
            error={toFormErrorText(form.errors.type)}
            isRequired
          />
          <div className={styles.field}>
            <DSText size="sm" weight="medium" component="span">
              {t("raise.severityLabel")}
            </DSText>
            <DSSegmentedControl<GapSeverity>
              value={form.values.severity}
              options={severityOptions}
              onChange={(value) => {
                form.setFieldValue("severity", value);
              }}
              ariaLabel={t("raise.severityLabel")}
              isFullWidth
            />
          </div>
          <div className={styles.field}>
            <DSText size="sm" weight="medium" component="span">
              {t("target.label")}
            </DSText>
            <DSSegmentedControl<GapTargetType>
              value={targetType}
              options={targetTypeOptions}
              onChange={handleTargetTypeChange}
              ariaLabel={t("target.label")}
              isFullWidth
            />
          </div>
          {targetType !== "story" && (
            <DSSelect<string>
              key={targetType}
              label={t("raise.targetRefLabel")}
              value={form.values.targetRef}
              options={targetOptions}
              onChange={(value) => {
                form.setFieldValue("targetRef", value);
              }}
              description={hasNoTargets ? t("raise.noTargets") : undefined}
              error={toFormErrorText(form.errors.targetRef)}
              isDisabled={isTargetLoading || hasNoTargets}
              isRequired
              isSearchable
            />
          )}
          {type === MISSING_TEST_DATA_TYPE && (
            <DSSelect<GapDataScope>
              label={t("dataScope.label")}
              value={form.values.dataScope}
              options={dataScopeOptions}
              onChange={(value) => {
                form.setFieldValue("dataScope", value);
              }}
              isClearable
            />
          )}
          <DSTextarea
            label={t("raise.questionLabel")}
            value={form.values.question}
            onChange={(value) => {
              form.setFieldValue("question", value);
            }}
            error={toFormErrorText(form.errors.question)}
            maxLength={MAX_QUESTION_LENGTH}
            isRequired
            isAutosize
          />
          <DSSelect<string>
            label={t("raise.assigneeLabel")}
            value={form.values.assigneeId}
            options={memberOptions}
            onChange={(value) => {
              form.setFieldValue("assigneeId", value);
              form.clearFieldError("assigneeId");
            }}
            placeholder={t("raise.assigneeAutomatic")}
            error={toFormErrorText(form.errors.assigneeId)}
            isClearable
            isSearchable
          />
        </DSStack>
      </form>
    </DSModal>
  );
};
