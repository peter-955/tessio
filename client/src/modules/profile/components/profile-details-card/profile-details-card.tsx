"use client";

import {
  DSAvatar,
  DSButton,
  DSCard,
  DSGroup,
  DSInput,
  DSStack,
  DSText,
  hasLength,
  isNotEmpty,
  useDSForm,
} from "@/components/design-system";
import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";
import { toFormErrorText } from "@/modules/auth/utils/form-error.util";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePatchMe } from "../../hooks/mutations/use-patch-me";
import { MAX_USER_NAME_LENGTH } from "../../typing/constants/profile.constant";
import type { NameValues } from "../../typing/types/name-values.type";
import { AvatarDialog } from "../avatar-dialog/avatar-dialog";
import styles from "./profile-details-card.module.scss";

export const ProfileDetailsCard: FC = () => {
  const { t } = useTranslation("profile");
  const currentUser = useCurrentUser();
  const { showSuccessToast } = useShowToast();
  const [isAvatarDialogOpened, setIsAvatarDialogOpened] = useState(false);
  const saveName = usePatchMe();
  const removeAvatar = usePatchMe();
  const isNameRequired = isNotEmpty(t("details.nameRequired"));
  const isNameShortEnough = hasLength({ max: MAX_USER_NAME_LENGTH }, t("details.nameTooLong"));
  const form = useDSForm<NameValues>({
    mode: "controlled",
    initialValues: { name: currentUser.name },
    validate: {
      name: (value) => {
        return isNameRequired(value) ?? isNameShortEnough(value.trim());
      },
    },
  });
  const isNameUnchanged = form.values.name.trim() === currentUser.name;

  const handleNameChange = (value: string): void => {
    form.setFieldValue("name", value);
  };

  const handleValidSubmit = (values: NameValues): void => {
    const name = values.name.trim();
    saveName.mutate(
      { name },
      {
        onSuccess: () => {
          form.setFieldValue("name", name);
          showSuccessToast(t("details.saved"));
        },
      },
    );
  };

  const handleOpenAvatarDialog = (): void => {
    setIsAvatarDialogOpened(true);
  };

  const handleCloseAvatarDialog = (): void => {
    setIsAvatarDialogOpened(false);
  };

  const handleRemoveAvatar = (): void => {
    removeAvatar.mutate(
      { avatarFileId: null },
      {
        onSuccess: () => {
          showSuccessToast(t("avatar.removed"));
        },
      },
    );
  };

  return (
    <DSCard title={t("details.title")}>
      <DSStack gap={5}>
        <DSGroup gap={4} isWrapping>
          <DSAvatar name={currentUser.name} src={currentUser.avatarUrl} size="xl" />
          <DSGroup gap={2} isWrapping>
            <DSButton type="default" icon="upload" onClick={handleOpenAvatarDialog}>
              {t("avatar.change")}
            </DSButton>
            {currentUser.avatarFileId !== null && (
              <DSButton
                type="ghost"
                icon="trash"
                isLoading={removeAvatar.isPending}
                onClick={handleRemoveAvatar}
              >
                {t("avatar.remove")}
              </DSButton>
            )}
          </DSGroup>
        </DSGroup>
        <DSStack gap={1}>
          <DSText size="sm" weight="medium">
            {t("details.email")}
          </DSText>
          <DSText color="muted" className={styles.email}>
            {currentUser.email}
          </DSText>
        </DSStack>
        <form onSubmit={form.onSubmit(handleValidSubmit)} noValidate className={styles.form}>
          <DSStack gap={3} align="start">
            <div className={styles.field}>
              <DSInput
                label={t("details.name")}
                value={form.values.name}
                onChange={handleNameChange}
                error={toFormErrorText(form.errors.name)}
                autoComplete="name"
                isRequired
              />
            </div>
            <DSButton
              type="primary"
              nativeType="submit"
              isLoading={saveName.isPending}
              isDisabled={isNameUnchanged}
            >
              {t("details.save")}
            </DSButton>
          </DSStack>
        </form>
      </DSStack>
      <AvatarDialog isOpened={isAvatarDialogOpened} onClose={handleCloseAvatarDialog} />
    </DSCard>
  );
};
