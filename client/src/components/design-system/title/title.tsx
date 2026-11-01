import { Title } from "@mantine/core";
import type { FC, ReactNode } from "react";
import { DS_TITLE_SIZES } from "../typing/constants/text.constant";
import type { DSTitleOrder, DSTitleType } from "../typing/types/text.type";

interface Props {
  children: ReactNode;
  order?: DSTitleOrder;
  type?: DSTitleType;
  className?: string;
}

export const DSTitle: FC<Props> = ({ children, order = 1, type = "page", className }) => {
  return (
    <Title order={order} fz={DS_TITLE_SIZES[type]} className={className}>
      {children}
    </Title>
  );
};
