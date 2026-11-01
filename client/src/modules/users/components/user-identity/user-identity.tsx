"use client";

import { DSAvatar, DSBadge, DSGroup, DSText } from "@/components/design-system";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { WorkspaceUser } from "../../typing/types/workspace-user.type";
import styles from "./user-identity.module.scss";

interface Props {
  user: WorkspaceUser;
  isCurrentUser: boolean;
  href?: string;
}

export const UserIdentity: FC<Props> = ({ user, isCurrentUser, href }) => {
  const { t } = useTranslation("users");

  return (
    <DSGroup gap={3} className={styles.identity}>
      <DSAvatar
        name={user.name}
        src={user.avatarUrl}
        isDeactivated={user.status === "deactivated"}
      />
      <div className={styles.details}>
        <DSGroup gap={2}>
          {href === undefined ? (
            <span className={styles.name}>{user.name}</span>
          ) : (
            <Link href={href} className={styles.name}>
              {user.name}
            </Link>
          )}
          {isCurrentUser && <DSBadge color="tessio">{t("you")}</DSBadge>}
        </DSGroup>
        <DSText size="sm" color="muted" component="span" className={styles.email}>
          {user.email}
        </DSText>
      </div>
    </DSGroup>
  );
};
