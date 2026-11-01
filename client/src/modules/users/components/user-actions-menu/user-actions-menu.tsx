"use client";

import { DSActionIcon, DSMenu, type DSMenuItem } from "@/components/design-system";
import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostResendInvite } from "../../hooks/mutations/use-post-resend-invite";
import type { UserConfirmAction } from "../../typing/types/user-action.type";
import type { WorkspaceUser } from "../../typing/types/workspace-user.type";
import { buildUserAccessPath } from "../../utils/user-path.util";
import { checkCanChangeRole, checkCanManageUser } from "../../utils/user-permission.util";

interface Props {
  user: WorkspaceUser;
  onConfirm: (action: UserConfirmAction) => void;
  onChangeRole: () => void;
  isOnAccessPage?: boolean;
}

export const UserActionsMenu: FC<Props> = ({
  user,
  onConfirm,
  onChangeRole,
  isOnAccessPage = false,
}) => {
  const { t } = useTranslation("users");
  const currentUser = useCurrentUser();
  const { showSuccessToast } = useShowToast();
  const resendInvite = usePostResendInvite({
    onSuccess: () => {
      showSuccessToast(t("toasts.inviteResent", { email: user.email }));
    },
  });
  const canManage = checkCanManageUser(currentUser, user);
  const canChangeRole = checkCanChangeRole(currentUser, user);

  const buildDeactivateItems = (): DSMenuItem[] => {
    return [
      { key: "deactivate-divider", type: "divider" },
      {
        key: "deactivate",
        label: t("actions.deactivate"),
        isDanger: true,
        onClick: () => {
          onConfirm("deactivate");
        },
      },
    ];
  };

  const buildManageItems = (): DSMenuItem[] => {
    if (!canManage) {
      return [];
    }

    if (user.status === "invited") {
      return [
        {
          key: "resend-invite",
          label: t("actions.resendInvite"),
          isDisabled: resendInvite.isPending,
          onClick: () => {
            resendInvite.mutate(user.id);
          },
        },
        ...buildDeactivateItems(),
      ];
    }

    if (user.status === "deactivated") {
      return [
        {
          key: "reactivate",
          label: t("actions.reactivate"),
          onClick: () => {
            onConfirm("reactivate");
          },
        },
      ];
    }

    return [
      ...(canChangeRole
        ? [{ key: "change-role", label: t("actions.changeRole"), onClick: onChangeRole }]
        : []),
      ...(user.isTwoFactorSetUp
        ? [
            {
              key: "reset-two-factor",
              label: t("actions.resetTwoFactor"),
              onClick: () => {
                onConfirm("resetTwoFactor");
              },
            },
          ]
        : []),
      ...buildDeactivateItems(),
    ];
  };

  const items: DSMenuItem[] = [
    ...(isOnAccessPage
      ? []
      : [
          {
            key: "view-access",
            label: t("actions.viewAccess"),
            href: buildUserAccessPath(user.id),
          },
        ]),
    ...buildManageItems(),
  ];
  const visibleItems = items[0]?.type === "divider" ? items.slice(1) : items;

  if (visibleItems.length === 0) {
    return null;
  }

  return (
    <DSMenu
      target={
        <DSActionIcon
          icon="dots"
          ariaLabel={t("actions.menu", { name: user.name })}
          isLoading={resendInvite.isPending}
        />
      }
      items={visibleItems}
    />
  );
};
