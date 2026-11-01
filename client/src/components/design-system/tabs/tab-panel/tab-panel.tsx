"use client";

import { Tabs } from "@mantine/core";
import type { FC, ReactNode } from "react";
import styles from "./tab-panel.module.scss";

interface Props {
  value: string;
  children: ReactNode;
}

export const DSTabPanel: FC<Props> = ({ value, children }) => {
  return (
    <Tabs.Panel value={value} className={styles.panel}>
      {children}
    </Tabs.Panel>
  );
};
