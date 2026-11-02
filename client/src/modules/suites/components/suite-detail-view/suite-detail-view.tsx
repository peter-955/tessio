"use client";

import {
  DSActionIcon,
  DSAlert,
  DSButton,
  DSButtonLink,
  DSCard,
  DSEmptyState,
  DSGroup,
  DSMenu,
  DSPageHeader,
  DSStack,
  DSText,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { checkCanStartManualRun } from "@/modules/manual-run/utils/manual-run-permission.util";
import { buildRunPath } from "@/modules/runs/utils/run-path.util";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useRef, useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { usePostSuiteArchive } from "../../hooks/mutations/use-post-suite-archive";
import { usePutSuiteCases } from "../../hooks/mutations/use-put-suite-cases";
import { useSuiteApiErrors } from "../../hooks/use-suite-api-errors";
import type { SuiteModalState } from "../../typing/types/suite-modal-state.type";
import type { SuiteCase, SuiteDetail } from "../../typing/types/suite.type";
import {
  listSuiteCaseIds,
  moveCaseId,
  orderSuiteCases,
  removeCaseId,
} from "../../utils/suite-cases.util";
import {
  buildNewSuiteRunPath,
  buildSuiteRunsPath,
  buildSuitesPath,
} from "../../utils/suite-path.util";
import { checkCanEditSuites } from "../../utils/suite-permission.util";
import { AddByFilterModal } from "../add-by-filter-modal/add-by-filter-modal";
import { AddCasesModal } from "../add-cases-modal/add-cases-modal";
import { ArchiveSuiteModal } from "../archive-suite-modal/archive-suite-modal";
import { RunSuiteCommand } from "../run-suite-command/run-suite-command";
import { SuiteCaseList } from "../suite-case-list/suite-case-list";
import { SuiteFormModal } from "../suite-form-modal/suite-form-modal";
import { SuiteLastRun } from "../suite-last-run/suite-last-run";
import styles from "./suite-detail-view.module.scss";

interface Props {
  suite: SuiteDetail;
}

export const SuiteDetailView: FC<Props> = ({ suite }) => {
  const { t } = useTranslation("suites");
  const project = useCurrentProject();
  const { showSuccessToast, showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const apiErrors = useSuiteApiErrors();
  const [modal, setModal] = useState<SuiteModalState>(null);
  const [pendingCaseIds, setPendingCaseIds] = useState<string[] | null>(null);
  const queuedCaseIdsRef = useRef<string[] | null>(null);
  const removedCasesRef = useRef<SuiteCase[]>([]);
  const isSavingRef = useRef(false);
  const isArchived = suite.archivedAt !== null;
  const canEdit = checkCanEditSuites(project) && !isArchived;
  const canStartManualRun =
    checkCanStartManualRun(project) &&
    !isArchived &&
    suite.readyCaseCount > 0 &&
    suite.runningRun === null;
  const caseIds = pendingCaseIds ?? listSuiteCaseIds(suite.cases);
  const cases = orderSuiteCases(suite.cases, caseIds);

  const handleSaveError = (error: ApiError): void => {
    isSavingRef.current = false;
    queuedCaseIdsRef.current = null;
    removedCasesRef.current = [];
    setPendingCaseIds(null);
    showErrorToast(resolveMessage(error, apiErrors));
  };

  const confirmRemovedCases = (savedCaseIds: readonly string[]): void => {
    const savedIds = new Set(savedCaseIds);
    const removedCases = removedCasesRef.current.filter((suiteCase) => {
      return !savedIds.has(suiteCase.testCaseId);
    });
    removedCasesRef.current = removedCasesRef.current.filter((suiteCase) => {
      return savedIds.has(suiteCase.testCaseId);
    });
    for (const suiteCase of removedCases) {
      showSuccessToast(t("cases.removed", { code: suiteCase.code }));
    }
  };

  const putCases = usePutSuiteCases(project.key, {
    isGlobalErrorToastDisabled: true,
    onError: handleSaveError,
    onSuccess: (_savedSuite, variables) => {
      confirmRemovedCases(variables.testCaseIds);
      const queuedCaseIds = queuedCaseIdsRef.current;
      if (queuedCaseIds !== null) {
        queuedCaseIdsRef.current = null;
        putCases.mutate({ suiteId: suite.id, testCaseIds: queuedCaseIds });
        return;
      }

      isSavingRef.current = false;
      setPendingCaseIds(null);
    },
  });
  const archiveSuite = usePostSuiteArchive(project.key, {
    isGlobalErrorToastDisabled: true,
    onError: (error) => {
      showErrorToast(resolveMessage(error, apiErrors));
    },
    onSuccess: () => {
      showSuccessToast(t("archive.done"));
      setModal(null);
    },
  });

  const saveCaseIds = (nextCaseIds: string[]): void => {
    setPendingCaseIds(nextCaseIds);
    if (isSavingRef.current) {
      queuedCaseIdsRef.current = nextCaseIds;
      return;
    }

    isSavingRef.current = true;
    putCases.mutate({ suiteId: suite.id, testCaseIds: nextCaseIds });
  };

  const handleMove = (fromIndex: number, toIndex: number): void => {
    saveCaseIds(moveCaseId(caseIds, fromIndex, toIndex));
  };

  const handleRemove = (suiteCase: SuiteCase): void => {
    removedCasesRef.current = [...removedCasesRef.current, suiteCase];
    saveCaseIds(removeCaseId(caseIds, suiteCase.testCaseId));
  };

  const renderModal = (): ReactNode => {
    switch (modal) {
      case "edit":
        return (
          <SuiteFormModal
            projectKey={project.key}
            suite={suite}
            onClose={() => {
              setModal(null);
            }}
          />
        );
      case "archive":
        return (
          <ArchiveSuiteModal
            name={suite.name}
            isArchiving={archiveSuite.isPending}
            onConfirm={() => {
              archiveSuite.mutate(suite.id);
            }}
            onClose={() => {
              setModal(null);
            }}
          />
        );
      case "addCases":
        return (
          <AddCasesModal
            projectKey={project.key}
            suite={suite}
            onClose={() => {
              setModal(null);
            }}
          />
        );
      case "addByFilter":
        return (
          <AddByFilterModal
            projectKey={project.key}
            suiteId={suite.id}
            onClose={() => {
              setModal(null);
            }}
          />
        );
      default:
        return null;
    }
  };

  const caseActions = canEdit && (
    <DSGroup gap={2} isWrapping>
      <DSButton
        type="default"
        icon="plus"
        size="sm"
        onClick={() => {
          setModal("addCases");
        }}
      >
        {t("cases.addCases")}
      </DSButton>
      <DSButton
        type="default"
        icon="filter"
        size="sm"
        onClick={() => {
          setModal("addByFilter");
        }}
      >
        {t("cases.addByFilter")}
      </DSButton>
    </DSGroup>
  );

  return (
    <>
      <div className={styles.back}>
        <DSButtonLink href={buildSuitesPath(project.key)} type="ghost">
          {t("detail.back")}
        </DSButtonLink>
      </div>
      <DSPageHeader
        title={suite.name}
        description={
          <span className={styles.description}>
            {suite.description !== null && <span>{suite.description}</span>}
            <span className={styles.summary}>
              {t("detail.summary", { count: suite.caseCount, ready: suite.readyCaseCount })}
            </span>
          </span>
        }
        actions={
          <DSGroup gap={2} isWrapping>
            {canStartManualRun && (
              <DSButtonLink href={buildNewSuiteRunPath(project.key, suite.id)} icon="runs">
                {t("detail.startManualRun")}
              </DSButtonLink>
            )}
            <DSButtonLink href={buildSuiteRunsPath(project.key, suite.id)} type="default">
              {t("detail.viewRuns")}
            </DSButtonLink>
            {canEdit && (
              <DSMenu
                target={<DSActionIcon icon="dots" ariaLabel={t("detail.actionsLabel")} />}
                items={[
                  {
                    key: "edit",
                    label: t("detail.edit"),
                    icon: "edit",
                    onClick: () => {
                      setModal("edit");
                    },
                  },
                  { key: "divider", type: "divider" },
                  {
                    key: "archive",
                    label: t("detail.archive"),
                    icon: "archive",
                    isDanger: true,
                    onClick: () => {
                      setModal("archive");
                    },
                  },
                ]}
              />
            )}
          </DSGroup>
        }
      />
      <DSStack gap={4}>
        {isArchived && (
          <DSAlert color="info" title={t("detail.archivedTitle")}>
            {t("detail.archivedDescription")}
          </DSAlert>
        )}
        {suite.runningRun !== null && (
          <DSAlert
            color="warning"
            title={t("detail.runningTitle")}
            action={
              <DSButtonLink href={buildRunPath(project.key, suite.runningRun.id)} size="sm">
                {t("detail.openRun")}
              </DSButtonLink>
            }
          >
            {t("detail.runningDescription")}
          </DSAlert>
        )}
        <div className={styles.layout}>
          <DSCard title={t("cases.title")} className={styles.cases}>
            <DSStack gap={3}>
              {caseActions}
              {cases.length === 0 ? (
                <DSEmptyState
                  title={t("cases.emptyTitle")}
                  description={
                    canEdit ? t("cases.emptyDescription") : t("cases.emptyReadOnlyDescription")
                  }
                  icon="testCases"
                  size="sm"
                />
              ) : (
                <SuiteCaseList
                  projectKey={project.key}
                  cases={cases}
                  canEdit={canEdit}
                  isSaving={putCases.isPending}
                  onMove={handleMove}
                  onRemove={handleRemove}
                />
              )}
            </DSStack>
          </DSCard>
          <DSStack gap={4}>
            {!isArchived && <RunSuiteCommand suite={suite} />}
            <DSCard title={t("list.columns.lastRun")}>
              {suite.lastRun === null ? (
                <DSText color="muted">{t("detail.neverRun")}</DSText>
              ) : (
                <SuiteLastRun projectKey={project.key} run={suite.lastRun} />
              )}
            </DSCard>
          </DSStack>
        </div>
      </DSStack>
      {renderModal()}
    </>
  );
};
