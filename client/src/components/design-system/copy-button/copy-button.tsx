"use client";

import { ActionIcon, Button, CopyButton, Tooltip, VisuallyHidden } from "@mantine/core";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { DSIcon } from "../icon/icon";

interface Props {
  value: string;
  label?: string;
  timeoutInMilliseconds?: number;
}

export const DSCopyButton: FC<Props> = ({ value, label, timeoutInMilliseconds = 2000 }) => {
  const { t } = useTranslation();

  return (
    <CopyButton value={value} timeout={timeoutInMilliseconds}>
      {({ copied: isCopied, copy: handleCopy }) => {
        const statusLabel = isCopied ? t("actions.copied") : t("actions.copy");
        const color = isCopied ? "teal" : "gray";
        const icon = <DSIcon name={isCopied ? "check" : "copy"} size={16} />;

        return (
          <>
            <Tooltip
              label={statusLabel}
              withArrow
              position="top"
              events={{ hover: true, focus: true, touch: false }}
            >
              {label ? (
                <Button
                  variant="default"
                  size="sm"
                  color={color}
                  leftSection={icon}
                  onClick={handleCopy}
                >
                  {label}
                </Button>
              ) : (
                <ActionIcon
                  variant="subtle"
                  size="md"
                  color={color}
                  aria-label={statusLabel}
                  onClick={handleCopy}
                >
                  {icon}
                </ActionIcon>
              )}
            </Tooltip>
            <VisuallyHidden role="status">{isCopied ? t("actions.copied") : ""}</VisuallyHidden>
          </>
        );
      }}
    </CopyButton>
  );
};
