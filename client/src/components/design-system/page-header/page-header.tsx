import type { FC, ReactNode } from "react";
import { DSGroup } from "../group/group";
import { DSStack } from "../stack/stack";
import { DSText } from "../text/text";
import { DSTitle } from "../title/title";
import styles from "./page-header.module.scss";

interface Props {
  title: string;
  description?: ReactNode;
  actions?: ReactNode;
}

export const DSPageHeader: FC<Props> = ({ title, description, actions }) => {
  return (
    <DSGroup justify="between" align="start" isWrapping className={styles.header}>
      <DSStack gap={1}>
        <DSTitle>{title}</DSTitle>
        {description && (
          <DSText color="muted" component="div">
            {description}
          </DSText>
        )}
      </DSStack>
      {actions && <DSGroup gap={2}>{actions}</DSGroup>}
    </DSGroup>
  );
};
