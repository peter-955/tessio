import { Code } from "@mantine/core";
import classNames from "classnames";
import type { FC } from "react";
import { DSCopyButton } from "../copy-button/copy-button";
import { DSGroup } from "../group/group";
import styles from "./code.module.scss";

interface Props {
  children: string;
  isBlock?: boolean;
  isCopyable?: boolean;
}

export const DSCode: FC<Props> = ({ children, isBlock = false, isCopyable = false }) => {
  if (!isCopyable || !isBlock) {
    return (
      <Code block={isBlock} className={styles.code}>
        {children}
      </Code>
    );
  }

  return (
    <DSGroup gap={2} align="start" className={styles.wrapper}>
      <Code block className={classNames(styles.code, styles.copyableCode)}>
        {children}
      </Code>
      <div className={styles.copy}>
        <DSCopyButton value={children} />
      </div>
    </DSGroup>
  );
};
