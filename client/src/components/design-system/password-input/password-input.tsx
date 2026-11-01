"use client";

import { PasswordInput } from "@mantine/core";
import type { ChangeEvent, FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";

interface Props {
  label: string;
  value: string;
  onChange: (value: string) => void;
  autoComplete: "current-password" | "new-password";
  description?: string;
  error?: ReactNode;
  isRequired?: boolean;
  isDisabled?: boolean;
  isAutoFocused?: boolean;
  visibilityToggleLabel?: string;
}

export const DSPasswordInput: FC<Props> = ({
  label,
  value,
  onChange,
  autoComplete,
  description,
  error,
  isRequired = false,
  isDisabled = false,
  isAutoFocused = false,
  visibilityToggleLabel,
}) => {
  const { t } = useTranslation();

  const handleChange = (event: ChangeEvent<HTMLInputElement>): void => {
    onChange(event.currentTarget.value);
  };

  return (
    <PasswordInput
      label={label}
      value={value}
      onChange={handleChange}
      autoComplete={autoComplete}
      description={description}
      error={error}
      required={isRequired}
      disabled={isDisabled}
      autoFocus={isAutoFocused}
      visibilityToggleFocusable
      visibilityToggleButtonProps={{
        "aria-label": visibilityToggleLabel ?? t("passwordInput.toggleVisibility"),
      }}
      size="sm"
    />
  );
};
