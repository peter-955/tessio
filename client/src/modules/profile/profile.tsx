"use client";

import { DSPageHeader, DSStack } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { ChangePasswordCard } from "./components/change-password-card/change-password-card";
import { PreferencesCard } from "./components/preferences-card/preferences-card";
import { ProfileDetailsCard } from "./components/profile-details-card/profile-details-card";
import { SessionsCard } from "./components/sessions-card/sessions-card";
import { TwoFactorCard } from "./components/two-factor-card/two-factor-card";
import styles from "./profile.module.scss";

export const ProfilePage: FC = () => {
  const { t } = useTranslation("profile");

  return (
    <>
      <DSPageHeader title={t("title")} description={t("description")} />
      <DSStack gap={5} className={styles.cards}>
        <ProfileDetailsCard />
        <PreferencesCard />
        <ChangePasswordCard />
        <TwoFactorCard />
        <SessionsCard />
      </DSStack>
    </>
  );
};
