"use client";

import {
  DSAlert,
  DSCheckbox,
  DSErrorState,
  DSInput,
  DSModal,
  DSSelect,
  DSSkeleton,
  DSStack,
  DSText,
} from "@/components/design-system";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useGetRunStoryOptions } from "@/modules/runs/hooks/queries/use-get-run-story-options";
import { useDebouncedValue } from "@/modules/stories/hooks/use-debounced-value";
import { useGetTestCases } from "@/modules/test-cases/hooks/queries/use-get-test-cases";
import { SEARCH_DEBOUNCE_MILLISECONDS } from "@/modules/test-cases/typing/constants/test-case.constant";
import { EMPTY_TEST_CASE_FILTERS } from "@/modules/test-cases/utils/test-case-filters.util";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { usePutSuiteCases } from "../../hooks/mutations/use-put-suite-cases";
import { useSuiteApiErrors } from "../../hooks/use-suite-api-errors";
import { MAX_SUITE_CASES } from "../../typing/constants/suite.constant";
import type { SuiteDetail } from "../../typing/types/suite.type";
import { appendCaseIds, listSuiteCaseIds } from "../../utils/suite-cases.util";
import styles from "./add-cases-modal.module.scss";

interface Props {
  projectKey: string;
  suite: SuiteDetail;
  onClose: () => void;
}

const LOADING_LINE_COUNT = 4;

export const AddCasesModal: FC<Props> = ({ projectKey, suite, onClose }) => {
  const { t } = useTranslation("suites");
  const { showSuccessToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const apiErrors = useSuiteApiErrors();
  const [searchText, setSearchText] = useState("");
  const [storyKey, setStoryKey] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<readonly string[]>([]);
  const query = useDebouncedValue(searchText, SEARCH_DEBOUNCE_MILLISECONDS);
  const { data: storyOptions = [] } = useGetRunStoryOptions(projectKey);
  const casesQuery = useGetTestCases(projectKey, { ...EMPTY_TEST_CASE_FILTERS, storyKey, query });
  const currentIds = listSuiteCaseIds(suite.cases);
  const nextIds = appendCaseIds(currentIds, selectedIds);
  const isOverLimit = nextIds.length > MAX_SUITE_CASES;
  const putCases = usePutSuiteCases(projectKey, {
    isGlobalErrorToastDisabled: true,
    onSuccess: () => {
      showSuccessToast(t("addCases.added", { count: selectedIds.length }));
      onClose();
    },
  });
  const cases = (casesQuery.data ?? []).filter((testCase) => {
    return testCase.status !== "deprecated";
  });

  const handleToggle = (caseId: string, isChecked: boolean): void => {
    setSelectedIds((current) => {
      return isChecked
        ? [...current, caseId]
        : current.filter((id) => {
            return id !== caseId;
          });
    });
  };

  const renderCases = (): ReactNode => {
    if (casesQuery.isPending) {
      return (
        <div role="status" aria-busy="true" aria-label={t("addCases.loading")}>
          <DSSkeleton height={36} lineCount={LOADING_LINE_COUNT} />
        </div>
      );
    }

    if (casesQuery.isError) {
      return (
        <DSErrorState
          title={t("addCases.loadError")}
          retryLabel={t("addCases.retry")}
          isRetrying={casesQuery.isFetching}
          onRetry={() => {
            void casesQuery.refetch();
          }}
        />
      );
    }

    if (cases.length === 0) {
      return <DSText color="muted">{t("addCases.noMatch")}</DSText>;
    }

    return (
      <fieldset className={styles.fieldset} disabled={putCases.isPending}>
        <legend className={styles.legend}>{t("addCases.listLabel")}</legend>
        <ul className={styles.list}>
          {cases.map((testCase) => {
            const isInSuite = currentIds.includes(testCase.id);

            return (
              <li key={testCase.id} className={styles.item}>
                <DSCheckbox
                  label={`${testCase.code} · ${testCase.title}`}
                  description={
                    isInSuite
                      ? `${testCase.storyKey} · ${t("addCases.alreadyAdded")}`
                      : testCase.storyKey
                  }
                  isChecked={isInSuite || selectedIds.includes(testCase.id)}
                  isDisabled={isInSuite || putCases.isPending}
                  onChange={(isChecked) => {
                    handleToggle(testCase.id, isChecked);
                  }}
                />
              </li>
            );
          })}
        </ul>
      </fieldset>
    );
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("addCases.title")}
      isCloseDisabled={putCases.isPending}
      action={{
        label: t("addCases.add"),
        icon: "plus",
        isLoading: putCases.isPending,
        isDisabled: selectedIds.length === 0 || isOverLimit,
        onClick: () => {
          putCases.mutate({ suiteId: suite.id, testCaseIds: nextIds });
        },
      }}
    >
      <DSStack gap={4}>
        <div className={styles.filters}>
          <DSInput
            label={t("addCases.search")}
            value={searchText}
            onChange={setSearchText}
            placeholder={t("addCases.searchPlaceholder")}
            autoComplete="off"
            isAutoFocused
          />
          <DSSelect<string>
            label={t("addCases.story")}
            value={storyKey}
            options={storyOptions}
            onChange={setStoryKey}
            placeholder={t("addCases.storyPlaceholder")}
            isSearchable
            isClearable
          />
        </div>
        {renderCases()}
        <DSText size="sm" color="muted" component="p" className={styles.count}>
          {t("addCases.selected", { count: selectedIds.length })}
        </DSText>
        {isOverLimit && (
          <DSAlert color="warning">{t("addCases.limit", { max: MAX_SUITE_CASES })}</DSAlert>
        )}
        {putCases.error !== null && (
          <DSAlert color="danger">{resolveMessage(putCases.error, apiErrors)}</DSAlert>
        )}
      </DSStack>
    </DSModal>
  );
};
