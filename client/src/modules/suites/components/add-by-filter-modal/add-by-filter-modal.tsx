"use client";

import {
  DSAlert,
  DSModal,
  DSMultiSelect,
  DSSelect,
  DSStack,
  DSText,
  type DSSelectOption,
} from "@/components/design-system";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useGetLabels } from "@/modules/labels/hooks/queries/use-get-labels";
import { useGetRunStoryOptions } from "@/modules/runs/hooks/queries/use-get-run-story-options";
import { useGetSprints } from "@/modules/sprints/hooks/queries/use-get-sprints";
import { TEST_CASE_PRIORITIES } from "@/modules/test-cases/typing/constants/test-case.constant";
import type { TestCasePriority } from "@/modules/test-cases/typing/types/test-case.type";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostSuiteCasesByFilter } from "../../hooks/mutations/use-post-suite-cases-by-filter";
import { useSuiteApiErrors } from "../../hooks/use-suite-api-errors";
import {
  EMPTY_SUITE_FILTER_VALUES,
  MAX_FILTER_LABELS,
} from "../../typing/constants/suite.constant";
import type { SuiteFilterValues } from "../../typing/types/suite-filter-values.type";
import { buildSuiteFilterRequest, checkHasSuiteFilter } from "../../utils/suite-request.util";

interface Props {
  projectKey: string;
  suiteId: string;
  onClose: () => void;
}

export const AddByFilterModal: FC<Props> = ({ projectKey, suiteId, onClose }) => {
  const { t } = useTranslation("suites");
  const { t: tTestCases } = useTranslation("testCases");
  const { showSuccessToast, showInfoToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const apiErrors = useSuiteApiErrors();
  const [values, setValues] = useState<SuiteFilterValues>(EMPTY_SUITE_FILTER_VALUES);
  const { data: labels = [] } = useGetLabels(projectKey);
  const { data: sprints = [] } = useGetSprints(projectKey);
  const { data: storyOptions = [] } = useGetRunStoryOptions(projectKey);
  const hasFilter = checkHasSuiteFilter(values);
  const addByFilter = usePostSuiteCasesByFilter(projectKey, {
    isGlobalErrorToastDisabled: true,
    onSuccess: ({ addedCount }) => {
      if (addedCount === 0) {
        showInfoToast(t("filter.noneAdded"));
      } else {
        showSuccessToast(t("filter.added", { count: addedCount }));
      }
      onClose();
    },
  });
  const labelOptions = labels.map((label): DSSelectOption<string> => {
    return { value: label.name, label: label.name };
  });
  const priorityOptions = TEST_CASE_PRIORITIES.map((priority): DSSelectOption<TestCasePriority> => {
    return { value: priority, label: tTestCases(`priority.${priority}`) };
  });
  const sprintOptions = sprints.map((sprint): DSSelectOption<string> => {
    return { value: sprint.id, label: sprint.name };
  });

  const updateValues = (update: Partial<SuiteFilterValues>): void => {
    setValues((current) => {
      return { ...current, ...update };
    });
    addByFilter.reset();
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("filter.title")}
      isCloseDisabled={addByFilter.isPending}
      action={{
        label: t("filter.add"),
        icon: "filter",
        isLoading: addByFilter.isPending,
        isDisabled: !hasFilter,
        onClick: () => {
          addByFilter.mutate({ suiteId, body: buildSuiteFilterRequest(values) });
        },
      }}
    >
      <DSStack gap={4}>
        <DSText size="sm">{t("filter.description")}</DSText>
        <DSMultiSelect<string>
          label={t("filter.labels")}
          description={t("filter.labelsDescription")}
          value={values.labels}
          options={labelOptions}
          onChange={(nextLabels) => {
            updateValues({ labels: nextLabels });
          }}
          placeholder={values.labels.length === 0 ? t("filter.labelsPlaceholder") : undefined}
          nothingFoundLabel={t("filter.nothingFound")}
          maxValues={MAX_FILTER_LABELS}
          isDisabled={addByFilter.isPending}
          isSearchable
        />
        <DSMultiSelect<TestCasePriority>
          label={t("filter.priorities")}
          value={values.priorities}
          options={priorityOptions}
          onChange={(priorities) => {
            updateValues({ priorities });
          }}
          placeholder={
            values.priorities.length === 0 ? t("filter.prioritiesPlaceholder") : undefined
          }
          isDisabled={addByFilter.isPending}
        />
        <DSSelect<string>
          label={t("filter.story")}
          value={values.storyKey}
          options={storyOptions}
          onChange={(storyKey) => {
            updateValues({ storyKey });
          }}
          placeholder={t("filter.storyPlaceholder")}
          nothingFoundLabel={t("filter.nothingFound")}
          isDisabled={addByFilter.isPending}
          isSearchable
          isClearable
        />
        <DSSelect<string>
          label={t("filter.sprint")}
          value={values.sprintId}
          options={sprintOptions}
          onChange={(sprintId) => {
            updateValues({ sprintId });
          }}
          placeholder={t("filter.sprintPlaceholder")}
          nothingFoundLabel={t("filter.nothingFound")}
          isDisabled={addByFilter.isPending}
          isSearchable
          isClearable
        />
        {!hasFilter && (
          <DSText size="sm" color="muted">
            {t("filter.required")}
          </DSText>
        )}
        {addByFilter.error !== null && (
          <DSAlert color="danger">{resolveMessage(addByFilter.error, apiErrors)}</DSAlert>
        )}
      </DSStack>
    </DSModal>
  );
};
