"use client";

import {
  DSActionIcon,
  DSBadge,
  DSMenu,
  DSTable,
  type DSMenuItem,
} from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { Environment } from "../../typing/types/environment.type";
import styles from "./environments-table.module.scss";

interface Props {
  environments: Environment[];
  defaultEnvironmentId: string | null;
  canManage: boolean;
  onEdit: (environment: Environment) => void;
  onArchive: (environment: Environment) => void;
  onUnarchive: (environment: Environment) => void;
  onDelete: (environment: Environment) => void;
}

export const EnvironmentsTable: FC<Props> = ({
  environments,
  defaultEnvironmentId,
  canManage,
  onEdit,
  onArchive,
  onUnarchive,
  onDelete,
}) => {
  const { t } = useTranslation("environments");

  const buildMenuItems = (environment: Environment): DSMenuItem[] => {
    const deleteItem: DSMenuItem = {
      key: "delete",
      label: t("actions.delete"),
      icon: "trash",
      isDanger: true,
      onClick: () => {
        onDelete(environment);
      },
    };

    if (environment.isArchived) {
      return [
        {
          key: "unarchive",
          label: t("actions.unarchive"),
          icon: "restore",
          onClick: () => {
            onUnarchive(environment);
          },
        },
        deleteItem,
      ];
    }

    return [
      {
        key: "edit",
        label: t("actions.edit"),
        icon: "edit",
        onClick: () => {
          onEdit(environment);
        },
      },
      {
        key: "archive",
        label: t("actions.archive"),
        icon: "archive",
        onClick: () => {
          onArchive(environment);
        },
      },
      { key: "divider", type: "divider" },
      deleteItem,
    ];
  };

  return (
    <DSTable label={t("table.ariaLabel")}>
      <caption className={styles.caption}>{t("table.ariaLabel")}</caption>
      <thead>
        <tr>
          <th scope="col">{t("table.name")}</th>
          <th scope="col">{t("table.baseUrl")}</th>
          <th scope="col">{t("table.healthCheckUrl")}</th>
          <th scope="col">{t("table.status")}</th>
          {canManage && (
            <th scope="col" className={styles.actionsCell}>
              <span className={styles.visuallyHidden}>{t("table.actions")}</span>
            </th>
          )}
        </tr>
      </thead>
      <tbody>
        {environments.map((environment) => {
          return (
            <tr key={environment.id}>
              <td>
                <span className={styles.nameCell}>
                  {environment.name}
                  {environment.id === defaultEnvironmentId && (
                    <DSBadge color="tessio">{t("table.default")}</DSBadge>
                  )}
                </span>
              </td>
              <td>
                <a
                  className={styles.link}
                  href={environment.baseUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {environment.baseUrl}
                </a>
              </td>
              <td>
                {environment.healthCheckUrl === null ? (
                  <span className={styles.muted}>{t("table.noValue")}</span>
                ) : (
                  <a
                    className={styles.link}
                    href={environment.healthCheckUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {environment.healthCheckUrl}
                  </a>
                )}
              </td>
              <td>
                {environment.isArchived ? (
                  <DSBadge color="gray">{t("status.archived")}</DSBadge>
                ) : (
                  <DSBadge color="green">{t("status.active")}</DSBadge>
                )}
              </td>
              {canManage && (
                <td className={styles.actionsCell}>
                  <DSMenu
                    items={buildMenuItems(environment)}
                    target={
                      <DSActionIcon
                        icon="dots"
                        ariaLabel={t("table.actionsFor", { name: environment.name })}
                      />
                    }
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
