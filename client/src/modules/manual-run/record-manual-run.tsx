"use client";

import { buildCaseReferences } from "@/components/case-sheet/utils/case-references.util";
import {
  DSAlert,
  DSButton,
  DSButtonLink,
  DSCard,
  DSCopyButton,
  DSErrorState,
  DSPageHeader,
  DSSkeleton,
  DSStack,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { UUID_PATTERN } from "@/modules/sprints/typing/constants/sprint.constant";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useQueryClient } from "@tanstack/react-query";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { CaseNavigator } from "./components/case-navigator/case-navigator";
import { CaseRecorder } from "./components/case-recorder/case-recorder";
import { FinishRunModal } from "./components/finish-run-modal/finish-run-modal";
import { IterationRecorder } from "./components/iteration-recorder/iteration-recorder";
import { RecordedCaseView } from "./components/recorded-case-view/recorded-case-view";
import { usePutManualCaseResult } from "./hooks/mutations/use-put-manual-case-result";
import {
  GET_MANUAL_RUN_KEY,
  useGetManualRun,
  type GetManualRunQueryKey,
} from "./hooks/queries/use-get-manual-run";
import { useManualRunApiErrors } from "./hooks/use-manual-run-api-errors";
import { useRunSecrets } from "./hooks/use-run-secrets";
import styles from "./record-manual-run.module.scss";
import { NOT_FOUND_STATUS } from "./typing/constants/manual-run.constant";
import type { CaseDraft } from "./typing/types/case-draft.type";
import type { ManualRun, ManualRunCase, ResultStatus } from "./typing/types/manual-run.type";
import type { StepDraft } from "./typing/types/step-draft.type";
import {
  buildCaseDraftKey,
  buildCaseResultRequest,
  createEmptyCaseDraft,
} from "./utils/case-result-request.util";
import { buildRunDetailPath, buildRunsPath } from "./utils/manual-run-path.util";
import { checkCanRecordRun, checkCanRevealRunSecrets } from "./utils/manual-run-permission.util";
import {
  checkIsCaseRecorded,
  checkIsDataDrivenCase,
  countRecordedCases,
  findFirstUnrecordedCase,
  findFirstUnrecordedIteration,
  findNextUnrecordedCase,
  findNextUnrecordedIteration,
  sortRunCases,
} from "./utils/run-case.util";
import { updateStepDraft } from "./utils/step-draft.util";

interface Props {
  runId: string;
}

export const RecordManualRunPage: FC<Props> = ({ runId }) => {
  const { t } = useTranslation("manualRun");
  const { t: tSuites } = useTranslation("suites");
  const { t: tDataRows } = useTranslation("dataRows");
  const project = useCurrentProject();
  const currentUser = useCurrentUser();
  const queryClient = useQueryClient();
  const resolveMessage = useResolveApiErrorMessage();
  const apiErrors = useManualRunApiErrors();
  const { showSuccessToast } = useShowToast();
  const isValidId = UUID_PATTERN.test(runId);
  const {
    data: run,
    error,
    isPending,
    isFetching,
    refetch,
  } = useGetManualRun(project.key, runId, isValidId);
  const recordResult = usePutManualCaseResult(project.key, runId);
  const [drafts, setDrafts] = useState<Record<string, CaseDraft>>({});
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [selectedIteration, setSelectedIteration] = useState<number | null>(null);
  const [isAllRecordedShown, setIsAllRecordedShown] = useState(false);
  const [isFinishOpened, setIsFinishOpened] = useState(false);
  const runSecrets = useRunSecrets(
    project.key,
    runId,
    run !== undefined && checkCanRevealRunSecrets(project, run, currentUser.id),
  );

  if (!isValidId || (run === undefined && error?.status === NOT_FOUND_STATUS)) {
    return (
      <DSErrorState
        title={t("record.notFound")}
        description={
          <DSButtonLink href={buildRunsPath(project.key)} type="default">
            {t("record.backToRuns")}
          </DSButtonLink>
        }
      />
    );
  }

  if (isPending) {
    return (
      <div aria-busy="true">
        <DSStack gap={5}>
          <DSSkeleton height={32} width="60%" />
          <DSSkeleton height={96} lineCount={3} />
        </DSStack>
      </div>
    );
  }

  if (run === undefined) {
    return (
      <DSErrorState
        title={t("record.loadError")}
        retryLabel={t("record.retry")}
        isRetrying={isFetching}
        onRetry={() => {
          void refetch();
        }}
      />
    );
  }

  const cases = sortRunCases(run.cases);
  const recordedCount = countRecordedCases(cases);
  const canRecord = checkCanRecordRun(project, run, currentUser.id);
  const currentCase =
    cases.find((runCase) => {
      return runCase.testCaseId === selectedCaseId;
    }) ??
    findFirstUnrecordedCase(cases) ??
    cases[0] ??
    null;
  const detailLink = (
    <DSButtonLink href={buildRunDetailPath(project.key, run.id)} type="default">
      {t("record.openDetail")}
    </DSButtonLink>
  );

  const updateDraft = (draftKey: string, update: (draft: CaseDraft) => CaseDraft): void => {
    setDrafts((currentDrafts) => {
      return {
        ...currentDrafts,
        [draftKey]: update(currentDrafts[draftKey] ?? createEmptyCaseDraft()),
      };
    });
  };

  const readDraft = (draftKey: string): CaseDraft => {
    return drafts[draftKey] ?? createEmptyCaseDraft();
  };

  const handleStepChange = (draftKey: string, order: number, changes: Partial<StepDraft>): void => {
    updateDraft(draftKey, (draft) => {
      return updateStepDraft(draft, order, changes);
    });
  };

  const handleStatusOverrideChange = (
    draftKey: string,
    statusOverride: ResultStatus | null,
  ): void => {
    updateDraft(draftKey, (draft) => {
      return { ...draft, statusOverride };
    });
  };

  const handleSelectCase = (testCaseId: string): void => {
    setSelectedCaseId(testCaseId);
    setSelectedIteration(null);
    setIsAllRecordedShown(false);
    recordResult.reset();
  };

  const handleSelectIteration = (iteration: number): void => {
    setSelectedIteration(iteration);
    recordResult.reset();
  };

  const handleSave = async (runCase: ManualRunCase, iteration: number | null): Promise<void> => {
    const draft = readDraft(buildCaseDraftKey(runCase.testCaseId, iteration));
    const steps =
      iteration === null
        ? runCase.steps
        : (runCase.iterations.find((candidate) => candidate.iteration === iteration)?.steps ??
          runCase.steps);

    try {
      await recordResult.mutateAsync({
        testCaseId: runCase.testCaseId,
        body: buildCaseResultRequest(draft, steps, iteration ?? 0),
      });
    } catch {
      return;
    }

    showSuccessToast(
      iteration === null
        ? t("record.saved", { code: runCase.code })
        : tDataRows("iteration.saved", { code: runCase.code, number: iteration + 1 }),
    );
    runSecrets.hideAll();
    const queryKey: GetManualRunQueryKey = [GET_MANUAL_RUN_KEY, project.key, runId];
    const refreshedRun = queryClient.getQueryData<ManualRun>(queryKey) ?? run;
    if (iteration !== null) {
      const refreshedCase =
        refreshedRun.cases.find((candidate) => candidate.testCaseId === runCase.testCaseId) ??
        runCase;
      const nextIteration = findNextUnrecordedIteration(refreshedCase, iteration);
      if (nextIteration !== null) {
        setSelectedIteration(nextIteration);
        return;
      }
    }

    const nextCase = findNextUnrecordedCase(refreshedRun.cases, runCase.testCaseId);
    setSelectedCaseId(nextCase?.testCaseId ?? runCase.testCaseId);
    setSelectedIteration(null);
    setIsAllRecordedShown(nextCase === null);
  };

  const renderNotice = (): ReactNode => {
    if (run.executor === "claude") {
      return (
        <DSAlert color="info" action={detailLink}>
          {t("record.claudeRun")}
        </DSAlert>
      );
    }

    if (run.status !== "running") {
      return (
        <DSAlert color="info" action={detailLink}>
          {t("record.runFinished")}
        </DSAlert>
      );
    }

    if (!canRecord && !project.isArchived) {
      return (
        <DSAlert color="info" action={detailLink}>
          {t("record.readOnly", { name: run.startedByName })}
        </DSAlert>
      );
    }

    return null;
  };

  const renderCurrentCase = (runCase: ManualRunCase): ReactNode => {
    const references = buildCaseReferences(
      run.data,
      runCase.files,
      runSecrets.revealedValues,
      run.environmentName,
    );
    const errorMessage =
      recordResult.error === null ? null : resolveMessage(recordResult.error, apiErrors);
    if (checkIsDataDrivenCase(runCase)) {
      const activeIteration =
        selectedIteration ??
        findFirstUnrecordedIteration(runCase) ??
        runCase.iterations[0]?.iteration ??
        0;

      return (
        <IterationRecorder
          key={runCase.testCaseId}
          runCase={runCase}
          activeIteration={activeIteration}
          readDraft={(iteration) => {
            return readDraft(buildCaseDraftKey(runCase.testCaseId, iteration));
          }}
          references={references}
          secretReveal={runSecrets.secretReveal}
          canRecord={canRecord}
          onSelectIteration={handleSelectIteration}
          onStepChange={(iteration, order, changes) => {
            handleStepChange(buildCaseDraftKey(runCase.testCaseId, iteration), order, changes);
          }}
          onStatusOverrideChange={(iteration, statusOverride) => {
            handleStatusOverrideChange(
              buildCaseDraftKey(runCase.testCaseId, iteration),
              statusOverride,
            );
          }}
          onCauseChange={(iteration, changes) => {
            updateDraft(buildCaseDraftKey(runCase.testCaseId, iteration), (draft) => {
              return { ...draft, ...changes };
            });
          }}
          onSave={(iteration) => {
            void handleSave(runCase, iteration);
          }}
          isSaving={recordResult.isPending}
          errorMessage={errorMessage}
        />
      );
    }

    if (!canRecord || checkIsCaseRecorded(runCase)) {
      return <RecordedCaseView runCase={runCase} references={references} />;
    }

    return (
      <CaseRecorder
        key={runCase.testCaseId}
        runCase={runCase}
        draft={readDraft(buildCaseDraftKey(runCase.testCaseId, null))}
        references={references}
        secretReveal={runSecrets.secretReveal}
        onStepChange={(order, changes) => {
          handleStepChange(runCase.testCaseId, order, changes);
        }}
        onStatusOverrideChange={(statusOverride) => {
          handleStatusOverrideChange(runCase.testCaseId, statusOverride);
        }}
        onCauseChange={(changes) => {
          updateDraft(runCase.testCaseId, (draft) => {
            return { ...draft, ...changes };
          });
        }}
        onSave={() => {
          void handleSave(runCase, null);
        }}
        isSaving={recordResult.isPending}
        errorMessage={errorMessage}
      />
    );
  };

  const isManualRunning = run.executor === "manual" && run.status === "running";

  return (
    <>
      <div className={styles.back}>
        <DSButtonLink href={buildRunsPath(project.key)} type="ghost">
          {t("record.backToRuns")}
        </DSButtonLink>
      </div>
      <DSPageHeader
        title={
          run.storyJiraKey === null
            ? tSuites("manualRun.recordTitle", { name: run.testSuiteName ?? run.testSuiteId ?? "" })
            : t("record.title", { storyKey: run.storyJiraKey })
        }
        description={
          <span className={styles.description}>
            <span className={styles.environment}>
              <span>{run.environmentName}</span>
              <a
                href={run.environmentBaseUrl}
                target="_blank"
                rel="noreferrer"
                className={styles.environmentLink}
                aria-label={t("record.openEnvironment", { environment: run.environmentName })}
              >
                {run.environmentBaseUrl}
              </a>
              <DSCopyButton value={run.environmentBaseUrl} />
            </span>
            <span>
              {`${t("record.startedBy", { name: run.startedByName })} · ${t("record.progress", {
                recorded: recordedCount,
                total: cases.length,
              })}`}
            </span>
          </span>
        }
        actions={
          canRecord && (
            <DSButton
              key={isAllRecordedShown ? "finish-ready" : "finish"}
              type={isAllRecordedShown ? "primary" : "outline"}
              icon="check"
              isAutoFocused={isAllRecordedShown}
              onClick={() => {
                setIsFinishOpened(true);
              }}
            >
              {t("finish.action")}
            </DSButton>
          )
        }
      />
      <DSStack gap={4}>
        {renderNotice()}
        {isAllRecordedShown && <DSAlert color="success">{t("record.allRecorded")}</DSAlert>}
        {isManualRunning && currentCase !== null && (
          <div className={styles.layout}>
            <CaseNavigator
              cases={cases}
              currentTestCaseId={currentCase.testCaseId}
              onSelect={handleSelectCase}
            />
            <DSCard className={styles.recorder}>{renderCurrentCase(currentCase)}</DSCard>
          </div>
        )}
      </DSStack>
      {isFinishOpened && (
        <FinishRunModal
          run={run}
          onClose={() => {
            setIsFinishOpened(false);
          }}
        />
      )}
    </>
  );
};
