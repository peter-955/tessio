"use client";

import { DSModal, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useDeleteApiToken } from "../../hooks/mutations/use-delete-api-token";
import type { ApiToken } from "../../typing/types/api-token.type";

interface Props {
  token: ApiToken | null;
  onClose: () => void;
}

export const RevokeTokenConfirm: FC<Props> = ({ token, onClose }) => {
  const { t } = useTranslation("connectClaude");
  const { mutate: revokeToken, isPending } = useDeleteApiToken({
    onSuccess: onClose,
    onError: (error) => {
      if (error.code === "NOT_FOUND") {
        onClose();
      }
    },
  });

  const handleConfirm = (): void => {
    if (token !== null) {
      revokeToken(token.id);
    }
  };

  return (
    <DSModal
      isOpened={token !== null}
      onClose={onClose}
      title={t("revoke.title")}
      isCloseDisabled={isPending}
      action={{
        label: t("revoke.confirm"),
        type: "danger",
        icon: "trash",
        isLoading: isPending,
        onClick: handleConfirm,
      }}
    >
      <DSText>
        {t("revoke.description", {
          name: token?.name ?? "",
          projectKey: token?.projectKey ?? "",
        })}
      </DSText>
    </DSModal>
  );
};
