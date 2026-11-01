"use client";

import {
  DSButton,
  DSEmptyState,
  DSErrorState,
  DSPageHeader,
  DSSkeleton,
} from "@/components/design-system";
import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { ChangeRoleModal } from "./components/change-role-modal/change-role-modal";
import { ConfirmUserActionModal } from "./components/confirm-user-action-modal/confirm-user-action-modal";
import { InviteUserModal } from "./components/invite-user-modal/invite-user-modal";
import { UserFilters } from "./components/user-filters/user-filters";
import { UserTable } from "./components/user-table/user-table";
import { useGetWorkspaceUsers } from "./hooks/queries/use-get-workspace-users";
import { useDebouncedValue } from "./hooks/use-debounced-value";
import { SEARCH_DEBOUNCE_MILLISECONDS } from "./typing/constants/user.constant";
import type { UserConfirmAction, UserConfirmTarget } from "./typing/types/user-action.type";
import type { UserFilters as UserFilterValues } from "./typing/types/user-filters.type";
import type { WorkspaceUser } from "./typing/types/workspace-user.type";
import { checkIsWorkspaceAdmin } from "./utils/user-permission.util";

const INITIAL_FILTERS: UserFilterValues = { status: null, workspaceRole: null, query: "" };

export const UsersPage: FC = () => {
  const { t } = useTranslation("users");
  const currentUser = useCurrentUser();
  const isWorkspaceAdmin = checkIsWorkspaceAdmin(currentUser.workspaceRole);
  const [filters, setFilters] = useState<UserFilterValues>(INITIAL_FILTERS);
  const [isInviteOpened, setIsInviteOpened] = useState(false);
  const [confirmTarget, setConfirmTarget] = useState<UserConfirmTarget | null>(null);
  const [changeRoleUser, setChangeRoleUser] = useState<WorkspaceUser | null>(null);
  const debouncedQuery = useDebouncedValue(filters.query, SEARCH_DEBOUNCE_MILLISECONDS);
  const { data, isPending, isError, isFetching, refetch } = useGetWorkspaceUsers(
    { ...filters, query: debouncedQuery },
    isWorkspaceAdmin,
  );

  if (!isWorkspaceAdmin) {
    return (
      <DSEmptyState
        title={t("noAccess.title")}
        description={t("noAccess.description")}
        icon="alertCircle"
      />
    );
  }

  const handleConfirm = (user: WorkspaceUser, action: UserConfirmAction): void => {
    setConfirmTarget({ user, action });
  };

  const renderList = (): ReactNode => {
    if (isPending) {
      return (
        <div aria-busy="true">
          <DSSkeleton lineCount={6} />
        </div>
      );
    }

    if (isError || data === undefined) {
      return (
        <DSErrorState
          title={t("loadError")}
          retryLabel={t("retry")}
          isRetrying={isFetching}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    if (data.length === 0) {
      return (
        <DSEmptyState
          title={t("empty.title")}
          description={t("empty.description")}
          icon="members"
        />
      );
    }

    return (
      <UserTable
        users={data}
        currentUserId={currentUser.id}
        onConfirm={handleConfirm}
        onChangeRole={setChangeRoleUser}
      />
    );
  };

  return (
    <>
      <DSPageHeader
        title={t("title")}
        description={t("description")}
        actions={
          <DSButton
            type="primary"
            icon="plus"
            onClick={() => {
              setIsInviteOpened(true);
            }}
          >
            {t("actions.invite")}
          </DSButton>
        }
      />
      <UserFilters filters={filters} onChange={setFilters} />
      {renderList()}
      <InviteUserModal
        isOpened={isInviteOpened}
        onClose={() => {
          setIsInviteOpened(false);
        }}
      />
      <ConfirmUserActionModal
        user={confirmTarget?.user ?? null}
        action={confirmTarget?.action ?? null}
        onClose={() => {
          setConfirmTarget(null);
        }}
      />
      <ChangeRoleModal
        user={changeRoleUser}
        onClose={() => {
          setChangeRoleUser(null);
        }}
      />
    </>
  );
};
