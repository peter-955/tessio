"use client";

import { DSGroup, DSInput, DSSelect, type DSSelectOption } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import {
  MAX_USER_QUERY_LENGTH,
  USER_STATUSES,
  WORKSPACE_ROLES,
} from "../../typing/constants/user.constant";
import type {
  UserStatusFilter,
  WorkspaceRoleFilter,
} from "../../typing/types/user-filter-option.type";
import type { UserFilters as UserFilterValues } from "../../typing/types/user-filters.type";
import styles from "./user-filters.module.scss";

interface Props {
  filters: UserFilterValues;
  onChange: (filters: UserFilterValues) => void;
}

export const UserFilters: FC<Props> = ({ filters, onChange }) => {
  const { t } = useTranslation("users");
  const statusOptions: DSSelectOption<UserStatusFilter>[] = [
    { value: "all", label: t("filters.all") },
    ...USER_STATUSES.map((status): DSSelectOption<UserStatusFilter> => {
      return { value: status, label: t(`statuses.${status}`) };
    }),
  ];
  const roleOptions: DSSelectOption<WorkspaceRoleFilter>[] = [
    { value: "all", label: t("filters.all") },
    ...WORKSPACE_ROLES.map((role): DSSelectOption<WorkspaceRoleFilter> => {
      return { value: role, label: t(`workspaceRoles.${role}`) };
    }),
  ];

  const handleQueryChange = (value: string): void => {
    onChange({ ...filters, query: value.slice(0, MAX_USER_QUERY_LENGTH) });
  };

  const handleStatusChange = (value: UserStatusFilter | null): void => {
    onChange({ ...filters, status: value === null || value === "all" ? null : value });
  };

  const handleRoleChange = (value: WorkspaceRoleFilter | null): void => {
    onChange({ ...filters, workspaceRole: value === null || value === "all" ? null : value });
  };

  return (
    <DSGroup gap={3} align="end" className={styles.filters}>
      <div className={styles.search}>
        <DSInput label={t("filters.search")} value={filters.query} onChange={handleQueryChange} />
      </div>
      <div className={styles.select}>
        <DSSelect<UserStatusFilter>
          label={t("filters.status")}
          value={filters.status ?? "all"}
          options={statusOptions}
          onChange={handleStatusChange}
        />
      </div>
      <div className={styles.select}>
        <DSSelect<WorkspaceRoleFilter>
          label={t("filters.role")}
          value={filters.workspaceRole ?? "all"}
          options={roleOptions}
          onChange={handleRoleChange}
        />
      </div>
    </DSGroup>
  );
};
