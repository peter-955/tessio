"use client";

import { CaseSheet } from "@/components/case-sheet/case-sheet";
import { CaseSheetSection } from "@/components/case-sheet/case-sheet-section/case-sheet-section";
import { buildCaseReferences } from "@/components/case-sheet/utils/case-references.util";
import { DSButton, DSSelect, type DSSelectOption } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import { DataRowsTable } from "@/modules/data-rows/components/data-rows-table/data-rows-table";
import { SharedStepReference } from "@/modules/shared-steps/components/shared-step-reference/shared-step-reference";
import { useRevealedSecrets } from "@/modules/test-data/hooks/use-revealed-secrets";
import { useGetEnvironments } from "@/shared/hooks/queries/use-get-environments";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetEffectiveTestData } from "../../hooks/queries/use-get-effective-test-data";
import type { TestCaseDetail } from "../../typing/types/test-case.type";
import {
  buildCaseCriteria,
  buildCaseDataValues,
  buildCaseFiles,
  mapRevealedValuesByKey,
} from "../../utils/case-sheet-data.util";
import styles from "./case-read-view.module.scss";

interface Props {
  detail: TestCaseDetail;
  canEdit: boolean;
  onEdit: () => void;
}

export const CaseReadView: FC<Props> = ({ detail, canEdit, onEdit }) => {
  const { t } = useTranslation("testCases");
  const { t: tDataRows } = useTranslation("dataRows");
  const project = useCurrentProject();
  const { parameters, dataRows } = detail.currentVersion;
  const { data: environments = [] } = useGetEnvironments(project.key);
  const [chosenEnvironmentId, setChosenEnvironmentId] = useState<string | null>(null);
  const defaultEnvironment =
    environments.find((environment) => environment.id === project.defaultEnvironmentId) ??
    environments[0];
  const environment =
    environments.find((candidate) => candidate.id === chosenEnvironmentId) ?? defaultEnvironment;
  const { data: items = [] } = useGetEffectiveTestData(project.key, environment?.id ?? null);
  const { revealedValueById, reveal, hide, isRevealing } = useRevealedSecrets(project.key);
  const itemIdByKey = new Map(items.map((item) => [item.key, item.id]));
  const environmentOptions = environments.map((candidate): DSSelectOption<string> => {
    return { value: candidate.id, label: candidate.name };
  });
  const references = buildCaseReferences(
    buildCaseDataValues(items),
    buildCaseFiles(detail),
    mapRevealedValuesByKey(items, revealedValueById),
    environment?.name ?? null,
  );

  const runForKey = (key: string, action: (itemId: string) => void): void => {
    const itemId = itemIdByKey.get(key);
    if (itemId !== undefined) {
      action(itemId);
    }
  };

  return (
    <div className={styles.view}>
      <div className={styles.toolbar}>
        {environmentOptions.length > 0 && (
          <div className={styles.environment}>
            <DSSelect<string>
              label={t("read.environment")}
              value={environment?.id ?? null}
              options={environmentOptions}
              onChange={setChosenEnvironmentId}
            />
          </div>
        )}
        {canEdit && (
          <DSButton type="outline" icon="edit" onClick={onEdit}>
            {t("read.edit")}
          </DSButton>
        )}
      </div>
      <CaseSheet
        criteria={buildCaseCriteria(detail)}
        businessValue={detail.currentVersion.businessValue}
        preconditions={detail.currentVersion.preconditions}
        steps={detail.currentVersion.steps}
        references={references}
        isStepListShown
        headingOrder={2}
        renderSharedStep={(sharedStepKey) => {
          return (
            <SharedStepReference
              projectKey={project.key}
              sharedStepKey={sharedStepKey}
              references={references}
            />
          );
        }}
        footer={
          parameters.length > 0 && (
            <CaseSheetSection
              headingOrder={2}
              title={tDataRows("table.title", { count: dataRows.length })}
            >
              <DataRowsTable parameters={parameters} dataRows={dataRows} />
            </CaseSheetSection>
          )
        }
        secretReveal={{
          canReveal: checkHasProjectCapability(project, "secret.reveal"),
          isRevealing: (key) => {
            const itemId = itemIdByKey.get(key);

            return itemId !== undefined && isRevealing(itemId);
          },
          onReveal: (key) => {
            runForKey(key, (itemId) => {
              void reveal(itemId);
            });
          },
          onHide: (key) => {
            runForKey(key, hide);
          },
        }}
      />
    </div>
  );
};
