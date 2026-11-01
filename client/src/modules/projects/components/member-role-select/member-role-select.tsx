"use client";

import { DSSelect, type DSSelectOption } from "@/components/design-system";
import type {
  ProjectMember,
  ProjectRole,
} from "@/components/project-context/typing/types/project.type";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePutProjectMember } from "../../hooks/mutations/use-put-project-member";
import { PROJECT_ROLES } from "../../typing/constants/project-role.constant";
import styles from "./member-role-select.module.scss";

interface Props {
  projectKey: string;
  member: ProjectMember;
}

export const MemberRoleSelect: FC<Props> = ({ projectKey, member }) => {
  const { t } = useTranslation("projects");
  const { showSuccessToast } = useShowToast();
  const { mutate: putMember, isPending } = usePutProjectMember(projectKey);
  const [pendingRole, setPendingRole] = useState<ProjectRole | null>(null);
  const roleOptions: DSSelectOption<ProjectRole>[] = PROJECT_ROLES.map((role) => {
    return { value: role, label: t(`roles.${role}`) };
  });

  const handleRoleChange = (role: ProjectRole | null): void => {
    if (role === null || role === member.role) {
      return;
    }

    setPendingRole(role);
    putMember(
      { userId: member.userId, role },
      {
        onSuccess: () => {
          showSuccessToast(t("members.roleUpdated"));
        },
        onSettled: () => {
          setPendingRole(null);
        },
      },
    );
  };

  return (
    <div className={styles.root}>
      <DSSelect<ProjectRole>
        label={t("members.roleFor", { name: member.name })}
        value={pendingRole ?? member.role}
        options={roleOptions}
        onChange={handleRoleChange}
        isDisabled={isPending || member.userStatus === "deactivated"}
      />
    </div>
  );
};
