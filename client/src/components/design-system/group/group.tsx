import { Group } from "@mantine/core";
import type { FC, ReactNode } from "react";
import { DS_ALIGN_VALUES, DS_JUSTIFY_VALUES } from "../typing/constants/layout.constant";
import type { DSAlign, DSJustify, DSSpace } from "../typing/types/layout.type";

interface Props {
  children: ReactNode;
  gap?: DSSpace;
  align?: DSAlign;
  justify?: DSJustify;
  isWrapping?: boolean;
  className?: string;
}

export const DSGroup: FC<Props> = ({
  children,
  gap = 3,
  align = "center",
  justify = "start",
  isWrapping = false,
  className,
}) => {
  return (
    <Group
      gap={`var(--space-${gap})`}
      align={DS_ALIGN_VALUES[align]}
      justify={DS_JUSTIFY_VALUES[justify]}
      wrap={isWrapping ? "wrap" : "nowrap"}
      className={className}
    >
      {children}
    </Group>
  );
};
