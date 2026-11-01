"use client";

import { EmptyState } from "@mantine/core";
import type { FC, ReactNode } from "react";
import { DSIcon } from "../icon/icon";
import type { DSIconName } from "../typing/types/icon.type";
import type { DSTitleOrder } from "../typing/types/text.type";
import { DS_EMPTY_STATE_ICON_SIZES } from "./empty-state.constant";
import styles from "./empty-state.module.scss";
import type { DSEmptyStateSize } from "./empty-state.type";

interface Props {
  title: string;
  description?: ReactNode;
  icon?: DSIconName;
  action?: ReactNode;
  size?: DSEmptyStateSize;
  titleOrder?: DSTitleOrder;
}

export const DSEmptyState: FC<Props> = ({
  title,
  description,
  icon = "inbox",
  action,
  size = "md",
  titleOrder,
}) => {
  return (
    <EmptyState
      size={size}
      variant="light"
      withIndicatorBackground
      icon={<DSIcon name={icon} size={DS_EMPTY_STATE_ICON_SIZES[size]} />}
      classNames={{
        root: size === "sm" ? styles.compact : styles.root,
        title: styles.title,
        description: styles.description,
      }}
    >
      <EmptyState.Title order={titleOrder}>{title}</EmptyState.Title>
      {description && <EmptyState.Description>{description}</EmptyState.Description>}
      {action && <EmptyState.Actions>{action}</EmptyState.Actions>}
    </EmptyState>
  );
};
