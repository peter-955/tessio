"use client";

import {
  DSAlert,
  DSButton,
  DSButtonLink,
  DSCard,
  DSEmptyState,
  DSErrorState,
  DSPageHeader,
  DSSegmentedControl,
  DSSelect,
  DSSkeleton,
  DSStack,
  type DSSegmentedOption,
  type DSSelectOption,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { OpenGapsBanner } from "@/modules/gaps/components/open-gaps-banner/open-gaps-banner";
import { SuiteSelect } from "@/modules/suites/components/suite-select/suite-select";
import { useGetSuite } from "@/modules/suites/hooks/queries/use-get-suite";
import { listRunnableSuiteCases } from "@/modules/suites/utils/suite-cases.util";
import { useGetEnvironments } from "@/shared/hooks/queries/use-get-environments";
import { useRouter } from "next/navigation";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { CasePicker } from "./components/case-picker/case-picker";
import { SuiteCasePicker } from "./components/suite-case-picker/suite-case-picker";
import { usePostManualRun } from "./hooks/mutations/use-post-manual-run";
import { useGetReadyTestCases } from "./hooks/queries/use-get-ready-test-cases";
import { useGetRunStories } from "./hooks/queries/use-get-run-stories";
import { useManualRunApiErrors } from "./hooks/use-manual-run-api-errors";
import styles from "./new-manual-run.module.scss";
import type { CasePickerItem } from "./typing/types/case-picker-item.type";
import type { CreateManualRunRequest, ReadyTestCase } from "./typing/types/manual-run.type";
import type { RunTarget } from "./typing/types/run-target.type";
import { pickDefaultEnvironmentId } from "./utils/default-environment.util";
import {
  buildRecordManualRunPath,
  buildRunsPath,
  buildStoryTestCasesPath,
} from "./utils/manual-run-path.util";
import { checkCanStartManualRun } from "./utils/manual-run-permission.util";

const NO_CASES: ReadyTestCase[] = [];

interface Props {
  initialStoryKey: string | null;
  initialSuiteId?: string | null;
}

export const NewManualRunPage: FC<Props> = ({ initialStoryKey, initialSuiteId = null }) => {
  const { t } = useTranslation("manualRun");
  const { t: tSuites } = useTranslation("suites");
  const router = useRouter();
  const project = useCurrentProject();
  const resolveMessage = useResolveApiErrorMessage();
  const apiErrors = useManualRunApiErrors();
  const [target, setTarget] = useState<RunTarget>(initialSuiteId === null ? "story" : "suite");
  const [storyKey, setStoryKey] = useState<string | null>(initialStoryKey);
  const [suiteId, setSuiteId] = useState<string | null>(initialSuiteId);
  const [pickedEnvironmentId, setPickedEnvironmentId] = useState<string | null>(null);
  const [excludedCaseIds, setExcludedCaseIds] = useState<readonly string[]>([]);
  const isSuiteTarget = target === "suite";
  const { data: stories = [] } = useGetRunStories(project.key);
  const environmentsQuery = useGetEnvironments(project.key);
  const casesQuery = useGetReadyTestCases(project.key, isSuiteTarget ? null : storyKey);
  const suiteQuery = useGetSuite(project.key, suiteId, isSuiteTarget);
  const createRun = usePostManualRun(project.key);
  const environments = environmentsQuery.data ?? [];
  const readyCases = casesQuery.data ?? NO_CASES;
  const suite = isSuiteTarget ? suiteQuery.data : undefined;
  const pickableIds = isSuiteTarget
    ? listRunnableSuiteCases(suite?.cases ?? []).map((suiteCase) => {
        return suiteCase.testCaseId;
      })
    : readyCases.map((testCase) => {
        return testCase.id;
      });
  const selectedCaseIds = pickableIds.filter((caseId) => {
    return !excludedCaseIds.includes(caseId);
  });
  const environmentId =
    pickedEnvironmentId ??
    pickDefaultEnvironmentId(environments, project.defaultEnvironmentId ?? null);
  const suiteApiErrors = {
    ...apiErrors,
    OPEN_GAPS_BLOCK_RUN: tSuites("manualRun.errors.openGaps"),
    SUITE_ALREADY_RUNNING: tSuites("manualRun.errors.alreadyRunning"),
    SUITE_EMPTY: tSuites("manualRun.errors.empty"),
    SUITE_ARCHIVED: tSuites("manualRun.errors.archived"),
  };

  if (!checkCanStartManualRun(project)) {
    return (
      <DSEmptyState
        title={t("new.cannotStart")}
        description={t("new.cannotStartDescription")}
        icon="lock"
        action={
          <DSButtonLink href={buildRunsPath(project.key)} type="default">
            {t("record.backToRuns")}
          </DSButtonLink>
        }
      />
    );
  }

  const storyOptions = stories.map((story): DSSelectOption<string> => {
    return { value: story.jiraKey, label: `${story.jiraKey} · ${story.title}` };
  });
  const isStoryListed = storyOptions.some((option) => {
    return option.value === storyKey;
  });
  const allStoryOptions =
    storyKey === null || isStoryListed
      ? storyOptions
      : [{ value: storyKey, label: storyKey }, ...storyOptions];
  const environmentOptions = environments.map((environment): DSSelectOption<string> => {
    return { value: environment.id, label: environment.name };
  });
  const targetOptions: DSSegmentedOption<RunTarget>[] = [
    { value: "story", label: tSuites("manualRun.targetStory") },
    { value: "suite", label: tSuites("manualRun.targetSuite") },
  ];
  const isTargetMissing = isSuiteTarget
    ? suiteId === null || suite === undefined || suite.runningRun !== null
    : storyKey === null;
  const isStartDisabled = isTargetMissing || environmentId === null || selectedCaseIds.length === 0;

  const resetSelection = (): void => {
    setExcludedCaseIds([]);
    createRun.reset();
  };

  const handleTargetChange = (nextTarget: RunTarget): void => {
    setTarget(nextTarget);
    resetSelection();
  };

  const handleStoryChange = (nextStoryKey: string | null): void => {
    setStoryKey(nextStoryKey);
    resetSelection();
  };

  const handleSuiteChange = (nextSuiteId: string | null): void => {
    setSuiteId(nextSuiteId);
    resetSelection();
  };

  const handleSelectionChange = (nextSelectedIds: string[]): void => {
    setExcludedCaseIds(
      pickableIds.filter((caseId) => {
        return !nextSelectedIds.includes(caseId);
      }),
    );
  };

  const buildRequest = (activeEnvironmentId: string): CreateManualRunRequest | null => {
    if (isSuiteTarget) {
      if (suiteId === null) {
        return null;
      }

      const isEveryCaseSelected = selectedCaseIds.length === pickableIds.length;

      return {
        suiteId,
        environmentId: activeEnvironmentId,
        ...(isEveryCaseSelected ? {} : { testCaseIds: selectedCaseIds }),
      };
    }

    return storyKey === null
      ? null
      : { storyKey, environmentId: activeEnvironmentId, testCaseIds: selectedCaseIds };
  };

  const handleStart = (): void => {
    const body = environmentId === null ? null : buildRequest(environmentId);
    if (body === null) {
      return;
    }

    createRun.mutate(body, {
      onSuccess: (createdRun) => {
        router.replace(buildRecordManualRunPath(project.key, createdRun.id));
      },
    });
  };

  const renderStoryCases = (activeStoryKey: string): ReactNode => {
    if (casesQuery.isPending) {
      return <DSSkeleton height={48} lineCount={3} />;
    }

    if (casesQuery.isError) {
      return (
        <DSErrorState
          title={t("record.loadError")}
          retryLabel={t("record.retry")}
          isRetrying={casesQuery.isFetching}
          onRetry={() => {
            void casesQuery.refetch();
          }}
        />
      );
    }

    if (readyCases.length === 0) {
      return (
        <DSEmptyState
          title={t("new.noReadyCases")}
          description={t("new.noReadyCasesDescription")}
          icon="file"
          size="sm"
          action={
            <DSButtonLink href={buildStoryTestCasesPath(project.key, activeStoryKey)}>
              {t("new.openTestCases")}
            </DSButtonLink>
          }
        />
      );
    }

    return (
      <CasePicker
        cases={readyCases.map((testCase): CasePickerItem => {
          return {
            id: testCase.id,
            label: `${testCase.code} · ${testCase.title} · ${t("new.stepCount", { count: testCase.stepCount })}`,
          };
        })}
        selectedIds={selectedCaseIds}
        onChange={handleSelectionChange}
        isDisabled={createRun.isPending}
      />
    );
  };

  const renderEnvironment = (): ReactNode => {
    if (environmentsQuery.isPending) {
      return <DSSkeleton height={36} />;
    }

    if (environments.length === 0) {
      return <DSAlert color="warning">{t("new.noEnvironments")}</DSAlert>;
    }

    return (
      <DSSelect<string>
        label={t("new.environment")}
        value={environmentId}
        options={environmentOptions}
        onChange={setPickedEnvironmentId}
        placeholder={t("new.environmentPlaceholder")}
        description={environmentId === null ? t("new.environmentRequired") : undefined}
        isRequired={environments.length > 1}
        isDisabled={createRun.isPending}
      />
    );
  };

  const renderStoryFields = (): ReactNode => {
    return (
      <>
        <DSSelect<string>
          label={t("new.story")}
          value={storyKey}
          options={allStoryOptions}
          onChange={handleStoryChange}
          placeholder={t("new.storyPlaceholder")}
          nothingFoundLabel={t("new.noStories")}
          isRequired
          isSearchable
          isDisabled={createRun.isPending}
        />
        {storyKey !== null && (
          <>
            <OpenGapsBanner projectKey={project.key} jiraKey={storyKey} />
            {renderEnvironment()}
            {renderStoryCases(storyKey)}
          </>
        )}
      </>
    );
  };

  const renderSuiteFields = (): ReactNode => {
    return (
      <>
        <SuiteSelect
          projectKey={project.key}
          value={suiteId}
          selectedSuite={suiteQuery.data ?? null}
          onChange={handleSuiteChange}
          label={tSuites("manualRun.suite")}
          placeholder={tSuites("manualRun.suitePlaceholder")}
          isRequired
          isDisabled={createRun.isPending}
        />
        {suiteId !== null && (
          <>
            {renderEnvironment()}
            <SuiteCasePicker
              projectKey={project.key}
              suite={suite}
              isPending={suiteQuery.isPending}
              isError={suiteQuery.isError}
              isFetching={suiteQuery.isFetching}
              onRetry={() => {
                void suiteQuery.refetch();
              }}
              selectedIds={selectedCaseIds}
              onChange={handleSelectionChange}
              isDisabled={createRun.isPending}
            />
          </>
        )}
      </>
    );
  };

  return (
    <>
      <div className={styles.back}>
        <DSButtonLink href={buildRunsPath(project.key)} type="ghost">
          {t("record.backToRuns")}
        </DSButtonLink>
      </div>
      <DSPageHeader title={t("new.title")} description={t("new.description")} />
      <DSCard className={styles.card}>
        <DSStack gap={5}>
          <DSSegmentedControl<RunTarget>
            value={target}
            options={targetOptions}
            onChange={handleTargetChange}
            ariaLabel={tSuites("manualRun.target")}
          />
          {isSuiteTarget ? renderSuiteFields() : renderStoryFields()}
          {createRun.error !== null && (
            <DSAlert color="danger">
              {resolveMessage(createRun.error, isSuiteTarget ? suiteApiErrors : apiErrors)}
            </DSAlert>
          )}
          <div className={styles.actions}>
            <DSButton
              type="primary"
              icon="runs"
              isDisabled={isStartDisabled}
              isLoading={createRun.isPending}
              onClick={handleStart}
            >
              {t("new.start")}
            </DSButton>
          </div>
        </DSStack>
      </DSCard>
    </>
  );
};
