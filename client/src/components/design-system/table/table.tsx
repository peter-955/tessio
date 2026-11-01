import type { FC, ReactNode } from "react";
import styles from "./table.module.scss";

interface Props {
  children: ReactNode;
  label?: string;
}

export const DSTable: FC<Props> = ({ children, label }) => {
  const hasLabel = label !== undefined;

  return (
    <div
      className={styles.wrapper}
      tabIndex={0}
      role={hasLabel ? "region" : undefined}
      aria-label={label}
    >
      <table className={styles.table}>{children}</table>
    </div>
  );
};
