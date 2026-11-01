"use client";

import { Modal } from "@mantine/core";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { DSButton } from "../button/button";
import { DSGroup } from "../group/group";
import type { DSModalAction } from "../typing/types/modal.type";
import styles from "./modal.module.scss";
import { useDSFocusReturn } from "./use-ds-focus-return";

interface Props {
  isOpened: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  action?: DSModalAction;
  cancelLabel?: string;
  hasCancelButton?: boolean;
  isClosedOnClickOutside?: boolean;
  isCloseDisabled?: boolean;
}

export const DSModal: FC<Props> = ({
  isOpened,
  onClose,
  title,
  children,
  action,
  cancelLabel,
  hasCancelButton = true,
  isClosedOnClickOutside = false,
  isCloseDisabled = false,
}) => {
  const { t } = useTranslation();
  useDSFocusReturn(isOpened);

  return (
    <Modal
      opened={isOpened}
      onClose={onClose}
      title={title}
      centered
      radius="lg"
      closeOnClickOutside={isClosedOnClickOutside && !isCloseDisabled}
      closeOnEscape={!isCloseDisabled}
      withCloseButton={!isCloseDisabled}
      closeButtonProps={{ "aria-label": t("actions.close") }}
    >
      {children}
      <DSGroup gap={2} justify="end" className={styles.footer}>
        {hasCancelButton && (
          <DSButton type="default" isDisabled={isCloseDisabled} onClick={onClose}>
            {cancelLabel ?? t("actions.cancel")}
          </DSButton>
        )}
        {action && (
          <DSButton
            type={action.type ?? "primary"}
            icon={action.icon}
            isLoading={action.isLoading}
            isDisabled={action.isDisabled}
            isAutoFocused={action.isAutoFocused}
            nativeType={action.formId ? "submit" : "button"}
            formId={action.formId}
            onClick={action.onClick}
          >
            {action.label}
          </DSButton>
        )}
      </DSGroup>
    </Modal>
  );
};
