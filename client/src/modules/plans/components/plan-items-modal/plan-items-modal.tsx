"use client";

import {
  DSAlert,
  DSModal,
  DSMultiSelect,
  DSSkeleton,
  DSStack,
  DSText,
} from "@/components/design-system";
import { useGetStories } from "@/modules/stories/hooks/queries/use-get-stories";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC, type ReactElement } from "react";
import { useTranslation } from "react-i18next";
import { usePutPlanItems } from "../../hooks/mutations/use-put-plan-items";
import { useGetPlanSuites } from "../../hooks/queries/use-get-plan-suites";
import { ALL_STORIES_FILTERS } from "../../typing/constants/plan-story-filters.constant";
import { MAX_PLAN_ITEMS } from "../../typing/constants/plan.constant";
import type { PlanItemsFormValues } from "../../typing/types/plan-items-form-values.type";
import type { PlanDetail } from "../../typing/types/plan.type";
import { buildStoryOptions, buildSuiteOptions } from "../../utils/plan-item-options.util";
import {
  buildPlanItemsFormValues,
  buildSetPlanItemsRequest,
  checkHasSamePlanItems,
  countPlanItems,
} from "../../utils/plan-request.util";

interface Props {
  projectKey: string;
  plan: PlanDetail;
  onClose: () => void;
}

export const PlanItemsModal: FC<Props> = ({ projectKey, plan, onClose }) => {
  const { t } = useTranslation("plans");
  const { showSuccessToast } = useShowToast();
  const [values, setValues] = useState<PlanItemsFormValues>(() => {
    return buildPlanItemsFormValues(plan.items);
  });
  const suites = useGetPlanSuites(projectKey);
  const stories = useGetStories(projectKey, ALL_STORIES_FILTERS);
  const putItems = usePutPlanItems(projectKey, plan.id, {
    onSuccess: () => {
      showSuccessToast(t("toasts.itemsSaved"));
      onClose();
    },
  });
  const isTooMany = countPlanItems(values) > MAX_PLAN_ITEMS;
  const isLoading = suites.isPending || stories.isPending;
  const isLoadFailed = suites.isError || stories.isError;

  const handleSave = (): void => {
    if (checkHasSamePlanItems(values, plan.items)) {
      onClose();
      return;
    }

    putItems.mutate(buildSetPlanItemsRequest(values));
  };

  const renderBody = (): ReactElement => {
    if (isLoading) {
      return (
        <div aria-busy="true">
          <DSSkeleton lineCount={4} />
        </div>
      );
    }

    if (isLoadFailed) {
      return <DSAlert color="danger">{t("items.loadError")}</DSAlert>;
    }

    return (
      <DSStack gap={4}>
        <DSText size="sm" color="muted">
          {t("items.description")}
        </DSText>
        <DSMultiSelect<string>
          label={t("items.suites")}
          value={values.suiteIds}
          options={buildSuiteOptions(suites.data ?? [], plan.items, (name) => {
            return t("items.archived", { name });
          })}
          onChange={(suiteIds) => {
            setValues((current) => {
              return { ...current, suiteIds };
            });
          }}
          placeholder={t("items.suitesPlaceholder")}
          nothingFoundLabel={t("items.nothingFound")}
        />
        <DSMultiSelect<string>
          label={t("items.stories")}
          value={values.storyIds}
          options={buildStoryOptions(stories.data ?? [], plan.items)}
          onChange={(storyIds) => {
            setValues((current) => {
              return { ...current, storyIds };
            });
          }}
          placeholder={t("items.storiesPlaceholder")}
          nothingFoundLabel={t("items.nothingFound")}
        />
        {isTooMany && (
          <DSAlert color="warning">{t("items.tooMany", { max: MAX_PLAN_ITEMS })}</DSAlert>
        )}
      </DSStack>
    );
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("items.modalTitle")}
      isCloseDisabled={putItems.isPending}
      action={{
        label: t("items.save"),
        isLoading: putItems.isPending,
        isDisabled: isLoading || isLoadFailed || isTooMany,
        onClick: handleSave,
      }}
    >
      {renderBody()}
    </DSModal>
  );
};
