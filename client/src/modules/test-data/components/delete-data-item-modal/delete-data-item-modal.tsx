"use client";

import { DSModal, DSText } from "@/components/design-system";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useDeleteDataItem } from "../../hooks/mutations/use-delete-data-item";
import type { DataItem } from "../../typing/types/data-item.type";

interface Props {
  projectKey: string;
  item: DataItem;
  scopeName: string;
  onClose: () => void;
  onDeleted: (item: DataItem) => void;
}

export const DeleteDataItemModal: FC<Props> = ({
  projectKey,
  item,
  scopeName,
  onClose,
  onDeleted,
}) => {
  const { t } = useTranslation("testData");
  const { showSuccessToast } = useShowToast();
  const deleteDataItem = useDeleteDataItem(projectKey, {
    onSuccess: () => {
      showSuccessToast(t("toasts.deleted"));
      onDeleted(item);
      onClose();
    },
  });

  const handleDelete = (): void => {
    deleteDataItem.mutate(item.id);
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("delete.title")}
      isCloseDisabled={deleteDataItem.isPending}
      action={{
        label: t("actions.delete"),
        type: "danger",
        icon: "trash",
        isLoading: deleteDataItem.isPending,
        onClick: handleDelete,
      }}
    >
      <DSText>{t("delete.message", { key: item.key, scope: scopeName })}</DSText>
    </DSModal>
  );
};
