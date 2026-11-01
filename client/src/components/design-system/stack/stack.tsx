import { Stack } from "@mantine/core";
import type { FC, ReactNode } from "react";
import { DS_ALIGN_VALUES, DS_JUSTIFY_VALUES } from "../typing/constants/layout.constant";
import type { DSAlign, DSJustify, DSSpace } from "../typing/types/layout.type";

interface Props {
  children: ReactNode;
  gap?: DSSpace;
  align?: DSAlign;
  justify?: DSJustify;
  className?: string;
}

export const DSStack: FC<Props> = ({
  children,
  gap = 3,
  align = "stretch",
  justify = "start",
  className,
}) => {
  return (
    <Stack
      gap={`var(--space-${gap})`}
      align={DS_ALIGN_VALUES[align]}
      justify={DS_JUSTIFY_VALUES[justify]}
      className={className}
    >
      {children}
    </Stack>
  );
};
