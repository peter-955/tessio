"use client";

import { Drawer } from "@mantine/core";
import type { FC, ReactNode } from "react";
import { useDSFocusReturn } from "../modal/use-ds-focus-return";
import { DS_DRAWER_WIDTHS } from "./drawer.constant";
import styles from "./drawer.module.scss";
import type { DSDrawerPosition, DSDrawerSize } from "./drawer.type";

interface Props {
  isOpened: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  position?: DSDrawerPosition;
  size?: DSDrawerSize;
  footer?: ReactNode;
  closeLabel: string;
}

export const DSDrawer: FC<Props> = ({
  isOpened,
  onClose,
  title,
  children,
  position = "right",
  size = "md",
  footer,
  closeLabel,
}) => {
  useDSFocusReturn(isOpened);

  return (
    <Drawer
      opened={isOpened}
      onClose={onClose}
      title={title}
      position={position}
      size={DS_DRAWER_WIDTHS[size]}
      closeButtonProps={{ "aria-label": closeLabel }}
      classNames={{
        content: styles.content,
        header: styles.header,
        title: styles.title,
        body: styles.body,
      }}
    >
      <div className={styles.main}>{children}</div>
      {footer && <div className={styles.footer}>{footer}</div>}
    </Drawer>
  );
};
