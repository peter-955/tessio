"use client";

import { DSModal, DSSelect, type DSSelectOption } from "@/components/design-system";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePutWorkspaceRole } from "../../hooks/mutations/use-put-workspace-role";
import { ASSIGNABLE_WORKSPACE_ROLES } from "../../typing/constants/user.constant";
import type {
  AssignableWorkspaceRole,
  WorkspaceUser,
} from "../../typing/types/workspace-user.type";
import { findAssignableWorkspaceRole } from "../../utils/workspace-role.util";

interface Props {
  user: WorkspaceUser | null;
  onClose: () => void;
}

export const ChangeRoleModal: FC<Props> = ({ user, onClose }) => {
  const { t } = useTranslation("users");
  const { showSuccessToast } = useShowToast();
  const [chosenRole, setChosenRole] = useState<AssignableWorkspaceRole | null>(null);
  const changeRole = usePutWorkspaceRole();

  if (user === null) {
    return null;
  }

  const currentRole = findAssignableWorkspaceRole(user.workspaceRole);
  const selectedRole = chosenRole ?? currentRole;
  const isUnchanged = selectedRole === null || selectedRole === currentRole;
  const roleOptions: DSSelectOption<AssignableWorkspaceRole>[] = ASSIGNABLE_WORKSPACE_ROLES.map(
    (role): DSSelectOption<AssignableWorkspaceRole> => {
      return { value: role, label: t(`workspaceRoles.${role}`) };
    },
  );

  const handleClose = (): void => {
    setChosenRole(null);
    onClose();
  };

  const handleSave = (): void => {
    if (selectedRole === null || isUnchanged) {
      return;
    }

    changeRole.mutate(
      { userId: user.id, workspaceRole: selectedRole },
      {
        onSuccess: () => {
          showSuccessToast(
            t("changeRole.success", {
              name: user.name,
              role: t(`workspaceRoles.${selectedRole}`),
            }),
          );
          handleClose();
        },
      },
    );
  };

  return (
    <DSModal
      isOpened
      onClose={handleClose}
      title={t("changeRole.title", { name: user.name })}
      isCloseDisabled={changeRole.isPending}
      action={{
        label: t("changeRole.submit"),
        isLoading: changeRole.isPending,
        isDisabled: isUnchanged,
        onClick: handleSave,
      }}
    >
      <DSSelect<AssignableWorkspaceRole>
        label={t("invite.role")}
        value={selectedRole}
        options={roleOptions}
        onChange={setChosenRole}
      />
    </DSModal>
  );
};
