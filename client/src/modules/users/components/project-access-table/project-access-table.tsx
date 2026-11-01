"use client";

import { DSBadge, DSTable } from "@/components/design-system";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { UserProjectAccess } from "../../typing/types/workspace-user.type";
import { buildProjectPath } from "../../utils/user-path.util";
import styles from "./project-access-table.module.scss";

interface Props {
  accesses: UserProjectAccess[];
}

export const ProjectAccessTable: FC<Props> = ({ accesses }) => {
  const { t } = useTranslation("users");

  return (
    <DSTable label={t("access.title")}>
      <thead>
        <tr>
          <th scope="col">{t("access.columns.project")}</th>
          <th scope="col">{t("access.columns.key")}</th>
          <th scope="col">{t("access.columns.role")}</th>
          <th scope="col">{t("access.columns.state")}</th>
        </tr>
      </thead>
      <tbody>
        {accesses.map((access) => {
          return (
            <tr key={access.projectId}>
              <td>
                <Link href={buildProjectPath(access.projectKey)}>{access.projectName}</Link>
              </td>
              <td className={styles.mono}>{access.projectKey}</td>
              <td>{t(`projectRoles.${access.role}`)}</td>
              <td>{access.isArchived && <DSBadge>{t("access.archived")}</DSBadge>}</td>
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
