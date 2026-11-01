import { PROJECT_SCOPE_ID } from "../typing/constants/test-data.constant";
import type { DataGridColumn } from "../typing/types/data-grid-column.type";
import type { Environment } from "../typing/types/environment.type";

const toColumn = (environment: Environment): DataGridColumn => {
  return { scopeId: environment.id, environment, isArchived: environment.isArchived };
};

export const buildDataGridColumns = (
  environments: readonly Environment[],
  isShowingArchived: boolean,
): DataGridColumn[] => {
  const activeColumns = environments.filter((environment) => !environment.isArchived).map(toColumn);
  const archivedColumns = isShowingArchived
    ? environments.filter((environment) => environment.isArchived).map(toColumn)
    : [];

  return [
    { scopeId: PROJECT_SCOPE_ID, environment: null, isArchived: false },
    ...activeColumns,
    ...archivedColumns,
  ];
};
