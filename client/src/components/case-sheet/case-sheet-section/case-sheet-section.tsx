"use client";

import { DSTitle, type DSTitleOrder } from "@/components/design-system";
import classNames from "classnames";
import type { FC, ReactNode } from "react";
import styles from "./case-sheet-section.module.scss";

interface Props {
  title: string;
  headingOrder: DSTitleOrder;
  children: ReactNode;
  isHighlighted?: boolean;
}

export const CaseSheetSection: FC<Props> = ({
  title,
  headingOrder,
  children,
  isHighlighted = false,
}) => {
  return (
    <section
      className={classNames(styles.section, isHighlighted && styles.highlighted)}
      aria-label={title}
    >
      <DSTitle order={headingOrder} type="section" className={styles.title}>
        {title}
      </DSTitle>
      {children}
    </section>
  );
};
