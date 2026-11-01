"use client";

import {
  DSButton,
  DSPageHeader,
  DSTabPanel,
  DSTabs,
  type DSTabItem,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { EnvironmentsPanel } from "@/modules/environments/environments";
import { useGetEnvironments } from "@/shared/hooks/queries/use-get-environments";
import { useRouter } from "next/navigation";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { DataGrid } from "./components/data-grid/data-grid";
import { DataItemModal } from "./components/data-item-modal/data-item-modal";
import { ImportWizard } from "./components/import-wizard/import-wizard";
import { TestDataTab } from "./typing/enums/test-data-tab.enum";
import type { DataItemCreatePreset } from "./typing/types/data-item-modal-state.type";
import { canEditDataItemKinds } from "./utils/data-item-capability.util";

interface Props {
  initialTab: TestDataTab;
}

interface CreateState {
  preset: DataItemCreatePreset | null;
}

export const TestDataPage: FC<Props> = ({ initialTab }) => {
  const { t } = useTranslation("testData");
  const router = useRouter();
  const project = useCurrentProject();
  const canEdit = canEditDataItemKinds(project, []);
  const [activeTab, setActiveTab] = useState(initialTab);
  const [createState, setCreateState] = useState<CreateState | null>(null);
  const [isImportOpened, setIsImportOpened] = useState(false);
  const environmentsQuery = useGetEnvironments(project.key, { isIncludingArchived: true });
  const environments = environmentsQuery.data ?? [];

  const tabItems: DSTabItem<TestDataTab>[] = [
    { value: TestDataTab.DATA, label: t("tabs.data"), icon: "testData" },
    { value: TestDataTab.ENVIRONMENTS, label: t("tabs.environments"), icon: "environments" },
  ];

  const handleTabChange = (tab: TestDataTab): void => {
    setActiveTab(tab);
    router.replace(`?tab=${tab}`, { scroll: false });
  };

  const handleCreate = (preset: DataItemCreatePreset | null): void => {
    setCreateState({ preset });
  };

  const openImport = (): void => {
    setIsImportOpened(true);
  };

  const closeImport = (): void => {
    setIsImportOpened(false);
  };

  const closeCreateModal = (): void => {
    setCreateState(null);
  };

  const showEnvironments = (): void => {
    handleTabChange(TestDataTab.ENVIRONMENTS);
  };

  return (
    <>
      <DSPageHeader
        title={t("title")}
        description={t("description")}
        actions={
          canEdit && (
            <>
              <DSButton type="default" icon="upload" onClick={openImport}>
                {t("actions.import")}
              </DSButton>
              <DSButton
                type="primary"
                icon="plus"
                onClick={() => {
                  handleCreate(null);
                }}
              >
                {t("actions.add")}
              </DSButton>
            </>
          )
        }
      />
      <DSTabs
        items={tabItems}
        value={activeTab}
        onChange={handleTabChange}
        ariaLabel={t("tabs.ariaLabel")}
      >
        <DSTabPanel value={TestDataTab.DATA}>
          <DataGrid
            environments={environmentsQuery.data}
            isEnvironmentsError={environmentsQuery.isError}
            isRetryingEnvironments={environmentsQuery.isFetching}
            onRetryEnvironments={() => {
              void environmentsQuery.refetch();
            }}
            onCreate={handleCreate}
            onImport={openImport}
            onManageEnvironments={showEnvironments}
          />
        </DSTabPanel>
        <DSTabPanel value={TestDataTab.ENVIRONMENTS}>
          <EnvironmentsPanel />
        </DSTabPanel>
      </DSTabs>
      {createState !== null && (
        <DataItemModal
          projectKey={project.key}
          state={{ mode: "create", preset: createState.preset }}
          environments={environments}
          onClose={closeCreateModal}
        />
      )}
      {isImportOpened && <ImportWizard environments={environments} onClose={closeImport} />}
    </>
  );
};
