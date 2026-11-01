"use client";

import { SegmentedControl } from "@mantine/core";
import type { ReactElement } from "react";
import type { DSSegmentedOption } from "../typing/types/segmented-control.type";

interface Props<T extends string> {
  value: T;
  options: DSSegmentedOption<T>[];
  onChange: (value: T) => void;
  ariaLabel: string;
  size?: "xs" | "sm";
  isFullWidth?: boolean;
}

export const DSSegmentedControl = <T extends string>({
  value,
  options,
  onChange,
  ariaLabel,
  size = "sm",
  isFullWidth = false,
}: Props<T>): ReactElement => {
  return (
    <SegmentedControl<T>
      value={value}
      data={options}
      onChange={onChange}
      size={size}
      fullWidth={isFullWidth}
      aria-label={ariaLabel}
    />
  );
};
