import { DSCard, DSStack, DSText, DSTitle } from "@/components/design-system";
import type { FC, ReactNode } from "react";
import styles from "./auth-card.module.scss";

interface Props {
  title: string;
  description?: string;
  children: ReactNode;
  footer?: ReactNode;
}

export const AuthCard: FC<Props> = ({ title, description, children, footer }) => {
  return (
    <DSCard className={styles.card}>
      <DSStack gap={5}>
        <DSStack gap={2}>
          <DSTitle order={1}>{title}</DSTitle>
          {description && (
            <DSText size="sm" color="muted">
              {description}
            </DSText>
          )}
        </DSStack>
        {children}
        {footer && <div className={styles.footer}>{footer}</div>}
      </DSStack>
    </DSCard>
  );
};
