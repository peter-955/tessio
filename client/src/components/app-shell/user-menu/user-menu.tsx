"use client";

import { DSAvatar, DSMenu, type DSMenuItem } from "@/components/design-system";
import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";
import { usePostSignOut } from "@/modules/auth/hooks/mutations/use-post-sign-out";
import { SignOutAllConfirm } from "@/modules/profile/components/sign-out-all-confirm/sign-out-all-confirm";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import styles from "./user-menu.module.scss";

export const UserMenu: FC = () => {
  const { t } = useTranslation();
  const { t: translateNavigation } = useTranslation("navigation");
  const currentUser = useCurrentUser();
  const { mutate: signOut, isPending: isSigningOut } = usePostSignOut();
  const [isSignOutAllOpened, setIsSignOutAllOpened] = useState(false);

  const items: DSMenuItem[] = [
    { key: "email", type: "label", label: currentUser.email },
    { key: "divider", type: "divider" },
    { key: "gapInbox", label: translateNavigation("gapInbox"), icon: "inbox", href: "/gaps" },
    { key: "profile", label: translateNavigation("profile"), icon: "user", href: "/profile" },
    {
      key: "connectClaude",
      label: translateNavigation("connectClaude"),
      icon: "key",
      href: "/connect-claude",
    },
    { key: "accountDivider", type: "divider" },
    {
      key: "signOut",
      label: t("appShell.userMenu.signOut"),
      icon: "logout",
      isDisabled: isSigningOut,
      onClick: () => {
        signOut();
      },
    },
    {
      key: "signOutAll",
      label: t("appShell.userMenu.signOutAll"),
      icon: "logout",
      isDanger: true,
      onClick: () => {
        setIsSignOutAllOpened(true);
      },
    },
  ];

  return (
    <>
      <DSMenu
        items={items}
        target={
          <button type="button" className={styles.target} aria-label={t("appShell.userMenu.label")}>
            <DSAvatar name={currentUser.name} src={currentUser.avatarUrl} size="sm" />
            <span className={styles.name}>{currentUser.name}</span>
          </button>
        }
      />
      <SignOutAllConfirm
        isOpened={isSignOutAllOpened}
        onClose={() => {
          setIsSignOutAllOpened(false);
        }}
      />
    </>
  );
};
