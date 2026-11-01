"use client";

import { PinInput } from "@mantine/core";
import type { FC } from "react";
import { useTranslation } from "react-i18next";

interface Props {
  value: string;
  onChange: (value: string) => void;
  ariaLabel: string;
  onComplete?: (value: string) => void;
  length?: number;
  hasError?: boolean;
  isDisabled?: boolean;
  isAutoFocused?: boolean;
}

export const DSPinInput: FC<Props> = ({
  value,
  onChange,
  ariaLabel,
  onComplete,
  length = 6,
  hasError = false,
  isDisabled = false,
  isAutoFocused = true,
}) => {
  const { t } = useTranslation();

  const getDigitInputProps = (index: number): { "aria-label": string } => {
    return {
      "aria-label": t("pinInput.digitLabel", {
        label: ariaLabel,
        position: index + 1,
        total: length,
      }),
    };
  };

  return (
    <PinInput
      value={value}
      onChange={onChange}
      onComplete={onComplete}
      length={length}
      error={hasError}
      disabled={isDisabled}
      autoFocus={isAutoFocused}
      type="number"
      inputMode="numeric"
      oneTimeCode
      manageFocus
      aria-label={ariaLabel}
      ariaLabel={ariaLabel}
      getInputProps={getDigitInputProps}
      size="sm"
    />
  );
};
