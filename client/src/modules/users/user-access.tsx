"use client";

import {
  DSAlert,
  DSBadge,
  DSButtonLink,
  DSEmptyState,
  DSErrorState,
  DSPageHeader,
  DSSkeleton,
  DSStack,
  DSTitle,
} from "@/components/design-system";
import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { ChangeRoleModal } from "./components/change-role-modal/change-role-modal";
import { ConfirmUserActionModal } from "./components/confirm-user-action-modal/confirm-user-action-modal";
import { ProjectAccessTable } from "./components/project-access-table/project-access-table";
import { UserActionsMenu } from "./components/user-actions-menu/user-actions-menu";
import { UserStatusBadge } from "./components/user-status-badge/user-status-badge";
import { useGetUserAccess } from "./hooks/queries/use-get-user-access";
import { useGetWorkspaceUser } from "./hooks/queries/use-get-workspace-user";
import {
  NOT_FOUND_STATUS,
  USERS_PATH,
  WORKSPACE_ROLE_BADGE_COLORS,
} from "./typing/constants/user.constant";
import type { UserConfirmAction } from "./typing/types/user-action.type";
import type { WorkspaceUser } from "./typing/types/workspace-user.type";
import styles from "./user-access.module.scss";
import { checkIsWorkspaceAdmin } from "./utils/user-permission.util";

interface Props {
  userId: string;
}

export const UserAccessPage: FC<Props> = ({ userId }) => {
  const { t } = useTranslation("users");
  const currentUser = useCurrentUser();
  const isWorkspaceAdmin = checkIsWorkspaceAdmin(currentUser.workspaceRole);
  const [confirmAction, setConfirmAction] = useState<UserConfirmAction | null>(null);
  const [changeRoleUser, setChangeRoleUser] = useState<WorkspaceUser | null>(null);
  const userQuery = useGetWorkspaceUser(userId, isWorkspaceAdmin);
  const accessQuery = useGetUserAccess(userId, isWorkspaceAdmin);

  if (!isWorkspaceAdmin) {
    return (
      <DSEmptyState
        title={t("noAccess.title")}
        description={t("noAccess.description")}
        icon="alertCircle"
      />
    );
  }

  const isNotFound =
    userQuery.error?.status === NOT_FOUND_STATUS || accessQuery.error?.status === NOT_FOUND_STATUS;

  if (isNotFound) {
    return (
      <DSEmptyState
        title={t("access.notFound.title")}
        icon="members"
        action={
          <DSButtonLink href={USERS_PATH} type="default">
            {t("access.back")}
          </DSButtonLink>
        }
      />
    );
  }

  const renderHeader = (): ReactNode => {
    if (userQuery.isPending) {
      return (
        <div aria-busy="true" className={styles.headerSkeleton}>
          <DSSkeleton lineCount={2} />
        </div>
      );
    }

    const user = userQuery.data;

    if (userQuery.isError || user === undefined) {
      return (
        <DSErrorState
          title={t("loadError")}
          retryLabel={t("retry")}
          isRetrying={userQuery.isFetching}
          onRetry={() => {
            void userQuery.refetch();
          }}
        />
      );
    }

    return (
      <>
        <DSPageHeader
          title={user.name}
          description={user.email}
          actions={
            <>
              <DSBadge color={WORKSPACE_ROLE_BADGE_COLORS[user.workspaceRole]}>
                {t(`workspaceRoles.${user.workspaceRole}`)}
              </DSBadge>
              <UserStatusBadge status={user.status} />
              <UserActionsMenu
                user={user}
                onConfirm={setConfirmAction}
                onChangeRole={() => {
                  setChangeRoleUser(user);
                }}
                isOnAccessPage
              />
            </>
          }
        />
        {checkIsWorkspaceAdmin(user.workspaceRole) && (
          <DSAlert color="info">{t("access.workspaceAdminNote")}</DSAlert>
        )}
      </>
    );
  };

  const renderAccessList = (): ReactNode => {
    if (accessQuery.isPending) {
      return (
        <div aria-busy="true">
          <DSSkeleton lineCount={4} />
        </div>
      );
    }

    const accesses = accessQuery.data;

    if (accessQuery.isError || accesses === undefined) {
      return (
        <DSErrorState
          title={t("access.loadError")}
          retryLabel={t("retry")}
          isRetrying={accessQuery.isFetching}
          onRetry={() => {
            void accessQuery.refetch();
          }}
        />
      );
    }

    if (accesses.length === 0) {
      return (
        <DSEmptyState
          title={t("access.empty.title")}
          description={t("access.empty.description")}
          icon="projects"
        />
      );
    }

    return <ProjectAccessTable accesses={accesses} />;
  };

  return (
    <DSStack gap={5}>
      <div>
        <DSButtonLink href={USERS_PATH} type="ghost">
          {t("access.back")}
        </DSButtonLink>
      </div>
      <DSStack gap={4}>{renderHeader()}</DSStack>
      <DSStack gap={3}>
        <DSTitle order={2} type="section">
          {t("access.title")}
        </DSTitle>
        {renderAccessList()}
      </DSStack>
      <ConfirmUserActionModal
        user={userQuery.data ?? null}
        action={confirmAction}
        onClose={() => {
          setConfirmAction(null);
        }}
      />
      <ChangeRoleModal
        user={changeRoleUser}
        onClose={() => {
          setChangeRoleUser(null);
        }}
      />
    </DSStack>
  );
};
