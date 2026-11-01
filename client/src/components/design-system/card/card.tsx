import { Card } from "@mantine/core";
import type { FC, ReactNode } from "react";
import { DSTitle } from "../title/title";
import styles from "./card.module.scss";

interface Props {
  children: ReactNode;
  title?: string;
  className?: string;
}

export const DSCard: FC<Props> = ({ children, title, className }) => {
  return (
    <Card withBorder padding="lg" radius="lg" className={className}>
      {title && (
        <DSTitle order={2} type="section" className={styles.title}>
          {title}
        </DSTitle>
      )}
      {children}
    </Card>
  );
};
