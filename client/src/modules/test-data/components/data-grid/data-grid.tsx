"use client";

import {
  DSAlert,
  DSBadge,
  DSButton,
  DSEmptyState,
  DSErrorState,
  DSGroup,
  DSInput,
  DSSkeleton,
  DSSwitch,
  DSTable,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import classNames from "classnames";
import { useMemo, useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useGetTestData } from "../../hooks/queries/use-get-test-data";
import { useRevealedSecrets } from "../../hooks/use-revealed-secrets";
import {
  DATA_GRID_SKELETON_ROW_COUNT,
  PROJECT_SCOPE_ID,
} from "../../typing/constants/test-data.constant";
import type { DataGridColumn } from "../../typing/types/data-grid-column.type";
import type {
  DataItemCreatePreset,
  DataItemModalState,
} from "../../typing/types/data-item-modal-state.type";
import type { DataItem } from "../../typing/types/data-item.type";
import type { Environment } from "../../typing/types/environment.type";
import { buildDataGridColumns } from "../../utils/build-data-grid-columns.util";
import {
  buildDataGridRows,
  filterDataGridRows,
  findRowKind,
  resolveDataItemScopeId,
} from "../../utils/build-data-grid-rows.util";
import { canEditDataItemKinds } from "../../utils/data-item-capability.util";
import { DataGridCell } from "../data-grid-cell/data-grid-cell";
import { DataItemModal } from "../data-item-modal/data-item-modal";
import { DeleteDataItemModal } from "../delete-data-item-modal/delete-data-item-modal";
import styles from "./data-grid.module.scss";

interface Props {
  environments: Environment[] | undefined;
  isEnvironmentsError: boolean;
  isRetryingEnvironments: boolean;
  onRetryEnvironments: () => void;
  onCreate: (preset: DataItemCreatePreset | null) => void;
  onImport: () => void;
  onManageEnvironments: () => void;
}

export const DataGrid: FC<Props> = ({
  environments: loadedEnvironments,
  isEnvironmentsError,
  isRetryingEnvironments,
  onRetryEnvironments,
  onCreate,
  onImport,
  onManageEnvironments,
}) => {
  const { t } = useTranslation("testData");
  const project = useCurrentProject();
  const canEdit = canEditDataItemKinds(project, []);
  const [search, setSearch] = useState("");
  const [isShowingArchived, setIsShowingArchived] = useState(false);
  const [editingState, setEditingState] = useState<DataItemModalState | null>(null);
  const [deletingItem, setDeletingItem] = useState<DataItem | null>(null);
  const revealedSecrets = useRevealedSecrets(project.key);
  const { hide } = revealedSecrets;
  const testData = useGetTestData(project.key);
  const environments = useMemo(() => loadedEnvironments ?? [], [loadedEnvironments]);
  const columns = useMemo(() => {
    return buildDataGridColumns(environments, isShowingArchived);
  }, [environments, isShowingArchived]);
  const rows = useMemo(() => buildDataGridRows(testData.data ?? []), [testData.data]);
  const visibleRows = useMemo(() => filterDataGridRows(rows, search), [rows, search]);
  const hasEnvironments = environments.some((environment) => !environment.isArchived);

  const findScopeName = (scopeId: string): string => {
    if (scopeId === PROJECT_SCOPE_ID) {
      return t("grid.allEnvironments");
    }

    return environments.find((environment) => environment.id === scopeId)?.name ?? scopeId;
  };

  const findColumnName = (column: DataGridColumn): string => {
    return column.environment?.name ?? t("grid.allEnvironments");
  };

  const handleEdit = (item: DataItem): void => {
    setEditingState({ mode: "edit", item });
  };

  const handleSaved = (item: DataItem): void => {
    hide(item.id);
  };

  const handleDeleted = (item: DataItem): void => {
    hide(item.id);
  };

  const closeEditModal = (): void => {
    setEditingState(null);
  };

  const closeDeleteModal = (): void => {
    setDeletingItem(null);
  };

  const editActions = canEdit && (
    <DSGroup gap={2} justify="center" isWrapping>
      <DSButton type="primary" icon="plus" onClick={() => onCreate(null)}>
        {t("actions.add")}
      </DSButton>
      <DSButton type="default" icon="upload" onClick={onImport}>
        {t("actions.import")}
      </DSButton>
    </DSGroup>
  );

  const renderTable = (): ReactNode => {
    if (visibleRows.length === 0) {
      return <DSEmptyState size="sm" icon="search" title={t("grid.noMatch")} />;
    }

    return (
      <div className={styles.grid}>
        <DSTable label={t("grid.ariaLabel")}>
          <caption className={styles.caption}>{t("grid.ariaLabel")}</caption>
          <thead>
            <tr>
              <th scope="col" className={classNames(styles.rowHeader, styles.keyHeader)}>
                {t("grid.key")}
              </th>
              {columns.map((column) => {
                return (
                  <th key={column.scopeId} scope="col">
                    <span className={styles.columnHeader}>
                      {findColumnName(column)}
                      {column.isArchived && <DSBadge>{t("grid.archived")}</DSBadge>}
                    </span>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {visibleRows.map((row) => {
              const rowKind = findRowKind(row);

              return (
                <tr key={row.key}>
                  <th scope="row" className={styles.rowHeader}>
                    <span className={styles.keyCell}>
                      <span className={styles.key}>{row.key}</span>
                      <DSBadge color={rowKind === "secret" ? "yellow" : "tessio"}>
                        {t(`kind.${rowKind}`)}
                      </DSBadge>
                    </span>
                  </th>
                  {columns.map((column) => {
                    return (
                      <td key={column.scopeId}>
                        <DataGridCell
                          dataKey={row.key}
                          rowKind={rowKind}
                          column={column}
                          scopeName={findColumnName(column)}
                          item={row.itemByScopeId[column.scopeId]}
                          projectItem={row.itemByScopeId[PROJECT_SCOPE_ID]}
                          revealedSecrets={revealedSecrets}
                          onCreate={onCreate}
                          onEdit={handleEdit}
                          onDelete={setDeletingItem}
                        />
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </DSTable>
      </div>
    );
  };

  const renderContent = (): ReactNode => {
    if (testData.isPending) {
      return (
        <div
          className={styles.loading}
          role="status"
          aria-busy="true"
          aria-label={t("grid.loading")}
        >
          <DSSkeleton height={36} lineCount={DATA_GRID_SKELETON_ROW_COUNT} />
        </div>
      );
    }

    if (testData.isError || testData.data === undefined) {
      return (
        <DSErrorState
          title={t("errors.loadFailed")}
          retryLabel={t("actions.retry")}
          isRetrying={testData.isFetching}
          onRetry={() => {
            void testData.refetch();
          }}
        />
      );
    }

    if (rows.length === 0) {
      return (
        <DSEmptyState
          title={t("empty.title")}
          description={t("empty.description")}
          icon="testData"
          action={editActions}
        />
      );
    }

    return (
      <>
        <DSGroup justify="between" align="end" isWrapping className={styles.toolbar}>
          <div className={styles.search}>
            <DSInput
              label={t("grid.search")}
              placeholder={t("grid.searchPlaceholder")}
              value={search}
              onChange={setSearch}
              autoComplete="off"
            />
          </div>
          <DSSwitch
            label={t("grid.showArchived")}
            isChecked={isShowingArchived}
            onChange={setIsShowingArchived}
          />
        </DSGroup>
        {renderTable()}
      </>
    );
  };

  return (
    <section aria-label={t("tabs.data")}>
      {isEnvironmentsError && (
        <div className={styles.hint}>
          <DSAlert
            color="warning"
            action={
              <DSButton
                type="default"
                size="sm"
                icon="refresh"
                isLoading={isRetryingEnvironments}
                onClick={onRetryEnvironments}
              >
                {t("actions.retry")}
              </DSButton>
            }
          >
            {t("errors.environmentsLoadFailed")}
          </DSAlert>
        </div>
      )}
      {loadedEnvironments !== undefined && !hasEnvironments && (
        <div className={styles.hint}>
          <DSAlert
            color="info"
            action={
              <DSButton type="default" size="sm" icon="environments" onClick={onManageEnvironments}>
                {t("grid.manageEnvironments")}
              </DSButton>
            }
          >
            {t("grid.noEnvironmentsHint")}
          </DSAlert>
        </div>
      )}
      {renderContent()}
      {editingState !== null && (
        <DataItemModal
          projectKey={project.key}
          state={editingState}
          environments={environments}
          onClose={closeEditModal}
          onSaved={handleSaved}
        />
      )}
      {deletingItem !== null && (
        <DeleteDataItemModal
          projectKey={project.key}
          item={deletingItem}
          scopeName={findScopeName(resolveDataItemScopeId(deletingItem))}
          onClose={closeDeleteModal}
          onDeleted={handleDeleted}
        />
      )}
    </section>
  );
};
