"use client";

import {
  DSAlert,
  DSButton,
  DSButtonLink,
  DSCard,
  DSEmptyState,
  DSErrorState,
  DSPageHeader,
  DSSelect,
  DSSkeleton,
  DSStack,
  type DSSelectOption,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { OpenGapsBanner } from "@/modules/gaps/components/open-gaps-banner/open-gaps-banner";
import { useGetEnvironments } from "@/shared/hooks/queries/use-get-environments";
import { useRouter } from "next/navigation";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { CasePicker } from "./components/case-picker/case-picker";
import { usePostManualRun } from "./hooks/mutations/use-post-manual-run";
import { useGetReadyTestCases } from "./hooks/queries/use-get-ready-test-cases";
import { useGetRunStories } from "./hooks/queries/use-get-run-stories";
import { useManualRunApiErrors } from "./hooks/use-manual-run-api-errors";
import styles from "./new-manual-run.module.scss";
import type { ReadyTestCase } from "./typing/types/manual-run.type";
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
}

export const NewManualRunPage: FC<Props> = ({ initialStoryKey }) => {
  const { t } = useTranslation("manualRun");
  const router = useRouter();
  const project = useCurrentProject();
  const resolveMessage = useResolveApiErrorMessage();
  const apiErrors = useManualRunApiErrors();
  const [storyKey, setStoryKey] = useState<string | null>(initialStoryKey);
  const [pickedEnvironmentId, setPickedEnvironmentId] = useState<string | null>(null);
  const [excludedCaseIds, setExcludedCaseIds] = useState<readonly string[]>([]);
  const { data: stories = [] } = useGetRunStories(project.key);
  const environmentsQuery = useGetEnvironments(project.key);
  const casesQuery = useGetReadyTestCases(project.key, storyKey);
  const createRun = usePostManualRun(project.key);
  const environments = environmentsQuery.data ?? [];
  const readyCases = casesQuery.data ?? NO_CASES;
  const selectedCaseIds = readyCases
    .filter((testCase) => {
      return !excludedCaseIds.includes(testCase.id);
    })
    .map((testCase) => {
      return testCase.id;
    });
  const environmentId =
    pickedEnvironmentId ??
    pickDefaultEnvironmentId(environments, project.defaultEnvironmentId ?? null);

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
  const isStartDisabled =
    storyKey === null || environmentId === null || selectedCaseIds.length === 0;

  const handleStoryChange = (nextStoryKey: string | null): void => {
    setStoryKey(nextStoryKey);
    setExcludedCaseIds([]);
    createRun.reset();
  };

  const handleSelectionChange = (nextSelectedIds: string[]): void => {
    setExcludedCaseIds(
      readyCases
        .filter((testCase) => {
          return !nextSelectedIds.includes(testCase.id);
        })
        .map((testCase) => {
          return testCase.id;
        }),
    );
  };

  const handleStart = (): void => {
    if (storyKey === null || environmentId === null) {
      return;
    }

    createRun.mutate(
      { storyKey, environmentId, testCaseIds: selectedCaseIds },
      {
        onSuccess: (createdRun) => {
          router.replace(buildRecordManualRunPath(project.key, createdRun.id));
        },
      },
    );
  };

  const renderCases = (activeStoryKey: string): ReactNode => {
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
        cases={readyCases}
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
              {renderCases(storyKey)}
            </>
          )}
          {createRun.error !== null && (
            <DSAlert color="danger">{resolveMessage(createRun.error, apiErrors)}</DSAlert>
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
