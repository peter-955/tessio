"use client";

import { DSActionIcon, DSAvatar, DSBadge, DSTable } from "@/components/design-system";
import type { ProjectMember } from "@/components/project-context/typing/types/project.type";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { MemberRoleSelect } from "../member-role-select/member-role-select";
import styles from "./members-table.module.scss";

interface Props {
  projectKey: string;
  members: ProjectMember[];
  canManage: boolean;
  onRemove: (member: ProjectMember) => void;
}

export const MembersTable: FC<Props> = ({ projectKey, members, canManage, onRemove }) => {
  const { t } = useTranslation("projects");
  const formatDate = useFormatDate();

  return (
    <DSTable label={t("members.title")}>
      <thead>
        <tr>
          <th scope="col">{t("members.columns.member")}</th>
          <th scope="col">{t("members.columns.status")}</th>
          <th scope="col">{t("members.columns.role")}</th>
          <th scope="col">{t("members.columns.added")}</th>
          {canManage && (
            <th scope="col">
              <span className={styles.visuallyHidden}>{t("members.columns.actions")}</span>
            </th>
          )}
        </tr>
      </thead>
      <tbody>
        {members.map((member) => {
          const isDeactivated = member.userStatus === "deactivated";
          return (
            <tr key={member.userId}>
              <td>
                <div className={styles.member}>
                  <DSAvatar name={member.name} size="sm" isDeactivated={isDeactivated} />
                  <div className={styles.identity}>
                    <span className={styles.name}>{member.name}</span>
                    <span className={styles.email}>{member.email}</span>
                  </div>
                </div>
              </td>
              <td>
                {member.userStatus === "invited" && (
                  <DSBadge color="yellow">{t("members.invited")}</DSBadge>
                )}
                {isDeactivated && <DSBadge>{t("members.deactivated")}</DSBadge>}
              </td>
              <td>
                {canManage ? (
                  <MemberRoleSelect projectKey={projectKey} member={member} />
                ) : (
                  t(`roles.${member.role}`)
                )}
              </td>
              <td className={styles.muted}>{formatDate(member.addedAt)}</td>
              {canManage && (
                <td className={styles.actionsCell}>
                  <DSActionIcon
                    icon="trash"
                    ariaLabel={t("members.remove", { name: member.name })}
                    onClick={() => {
                      onRemove(member);
                    }}
                  />
                </td>
              )}
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
