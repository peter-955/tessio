"use client";

import { DSTable } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { UserConfirmAction } from "../../typing/types/user-action.type";
import type { WorkspaceUser } from "../../typing/types/workspace-user.type";
import { buildUserAccessPath } from "../../utils/user-path.util";
import { UserActionsMenu } from "../user-actions-menu/user-actions-menu";
import { UserIdentity } from "../user-identity/user-identity";
import { UserStatusBadge } from "../user-status-badge/user-status-badge";
import styles from "./user-table.module.scss";

interface Props {
  users: WorkspaceUser[];
  currentUserId: string;
  onConfirm: (user: WorkspaceUser, action: UserConfirmAction) => void;
  onChangeRole: (user: WorkspaceUser) => void;
}

export const UserTable: FC<Props> = ({ users, currentUserId, onConfirm, onChangeRole }) => {
  const { t } = useTranslation("users");

  const renderTwoFactor = (user: WorkspaceUser): string => {
    if (user.status === "invited") {
      return "—";
    }

    return user.isTwoFactorSetUp ? t("twoFactor.setUp") : t("twoFactor.notSetUp");
  };

  return (
    <DSTable label={t("title")}>
      <thead>
        <tr>
          <th scope="col">{t("columns.user")}</th>
          <th scope="col">{t("columns.role")}</th>
          <th scope="col">{t("columns.status")}</th>
          <th scope="col">{t("columns.twoFactor")}</th>
          <th scope="col" className={styles.actionsColumn}>
            <span className={styles.visuallyHidden}>{t("columns.actions")}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        {users.map((user) => {
          return (
            <tr key={user.id}>
              <td>
                <UserIdentity
                  user={user}
                  isCurrentUser={user.id === currentUserId}
                  href={buildUserAccessPath(user.id)}
                />
              </td>
              <td>{t(`workspaceRoles.${user.workspaceRole}`)}</td>
              <td>
                <UserStatusBadge status={user.status} />
              </td>
              <td className={styles.muted}>{renderTwoFactor(user)}</td>
              <td className={styles.actionsColumn}>
                <UserActionsMenu
                  user={user}
                  onConfirm={(action) => {
                    onConfirm(user, action);
                  }}
                  onChangeRole={() => {
                    onChangeRole(user);
                  }}
                />
              </td>
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
